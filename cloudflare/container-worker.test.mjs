import { createExecutionContext } from 'cloudflare:test';
import { beforeEach, describe, expect, it } from 'vitest';

import worker from './container-worker.mjs';

const ORIGIN = 'https://mcp.lee.locker';
const MCP_URL = `${ORIGIN}/mcp`;
const LICENSE_KEY = 'ML-ABCD-EFGH-JKLM-NPQR';
const MASTER_KEY = 'internal-master-key';

class FakeKv {
  constructor(entries = {}) {
    this.entries = new Map(Object.entries(entries));
  }

  async get(key, options) {
    const value = this.entries.get(key);
    if (value === undefined) return null;
    if (options?.type === 'json') return JSON.parse(value);
    return value;
  }

  async put(key, value) {
    this.entries.set(key, String(value));
  }

  async delete(key) {
    this.entries.delete(key);
  }

  async list({ prefix = '' } = {}) {
    const keys = [...this.entries.keys()]
      .filter((key) => key.startsWith(prefix))
      .map((name) => ({ name }));
    return { keys, list_complete: true };
  }
}

function activeLicenseRecord() {
  return JSON.stringify({
    status: 'active',
    productKey: 'mcp_access',
  });
}

function makeEnv() {
  const forwarded = [];
  const container = {
    async startAndWaitForPorts() {},
    async fetch(request) {
      forwarded.push(request.clone());
      return Response.json({
        method: request.method,
        path: new URL(request.url).pathname,
        authorization: request.headers.get('Authorization'),
        body: request.method === 'POST' ? await request.clone().json() : null,
      });
    },
  };

  return {
    env: {
      HTTP_API_KEY: MASTER_KEY,
      MCP_DAILY_QUOTA: '200',
      LICENSES: new FakeKv({
        [`license:${LICENSE_KEY}`]: activeLicenseRecord(),
      }),
      OAUTH_KV: new FakeKv(),
      MINGLI_CONTAINER: {
        getByName() {
          return container;
        },
      },
    },
    forwarded,
  };
}

async function fetchWorker(request, env) {
  return worker.fetch(request, env, createExecutionContext());
}

function mcpRequest(method, authorization) {
  const headers = { 'Content-Type': 'application/json' };
  if (authorization) headers.Authorization = authorization;
  return new Request(MCP_URL, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method,
      params: method === 'tools/call' ? { name: 'bazi_chart', arguments: {} } : {},
    }),
  });
}

function extractCsrf(html) {
  return html.match(/name="csrf" value="([^"]+)"/)?.[1];
}

function extractCookie(response) {
  return response.headers.get('Set-Cookie')?.split(';', 1)[0];
}

function base64Url(bytes) {
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replaceAll('+', '-').replaceAll('/', '_').replace(/=+$/, '');
}

async function sha256Base64Url(value) {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value));
  return base64Url(new Uint8Array(digest));
}

describe('MCP OAuth gateway', () => {
  let env;
  let forwarded;

  beforeEach(() => {
    ({ env, forwarded } = makeEnv());
  });

  it('keeps MCP discovery free and forwards it with the internal key', async () => {
    const response = await fetchWorker(mcpRequest('tools/list'), env);

    expect(response.status).toBe(200);
    expect(forwarded).toHaveLength(1);
    expect((await response.json()).authorization).toBe(`Bearer ${MASTER_KEY}`);
  });

  it('keeps server/discover free (2026-07-28 stateless capability discovery)', async () => {
    const response = await fetchWorker(mcpRequest('server/discover'), env);

    expect(response.status).toBe(200);
    expect(forwarded).toHaveLength(1);
    expect((await response.json()).authorization).toBe(`Bearer ${MASTER_KEY}`);
  });

  it('does not inject the internal key into non-MCP container routes', async () => {
    const response = await fetchWorker(new Request(`${ORIGIN}/stats`), env);

    expect(response.status).toBe(200);
    expect((await response.json()).authorization).toBeNull();
  });

  it('challenges an unauthorized tool call with protected-resource metadata', async () => {
    const response = await fetchWorker(mcpRequest('tools/call'), env);

    expect(response.status).toBe(401);
    expect(response.headers.get('WWW-Authenticate')).toContain(
      `resource_metadata="${ORIGIN}/.well-known/oauth-protected-resource/mcp"`,
    );
    expect(forwarded).toHaveLength(0);
  });

  it('publishes OAuth and protected-resource discovery metadata', async () => {
    const authorizationResponse = await fetchWorker(
      new Request(`${ORIGIN}/.well-known/oauth-authorization-server`),
      env,
    );
    const protectedResponse = await fetchWorker(
      new Request(`${ORIGIN}/.well-known/oauth-protected-resource/mcp`),
      env,
    );

    expect(authorizationResponse.status).toBe(200);
    expect(await authorizationResponse.json()).toMatchObject({
      authorization_endpoint: `${ORIGIN}/authorize`,
      token_endpoint: `${ORIGIN}/token`,
      registration_endpoint: `${ORIGIN}/register`,
      code_challenge_methods_supported: ['S256'],
    });
    expect(await protectedResponse.json()).toMatchObject({
      resource: MCP_URL,
      authorization_servers: [ORIGIN],
      scopes_supported: ['mcp:tools'],
    });
    expect(forwarded).toHaveLength(0);
  });

  it('keeps a valid raw license working and counts its tool call', async () => {
    const response = await fetchWorker(
      mcpRequest('tools/call', `Bearer ${LICENSE_KEY.toLowerCase()}`),
      env,
    );

    expect(response.status).toBe(200);
    expect((await response.json()).authorization).toBe(`Bearer ${MASTER_KEY}`);
    const quotaKeys = [...env.LICENSES.entries.keys()].filter((key) =>
      key.startsWith(`mcpquota:${LICENSE_KEY}:`),
    );
    expect(quotaKeys).toHaveLength(1);
    expect(await env.LICENSES.get(quotaKeys[0])).toBe('1');
  });

  it('uses a CSRF-protected license consent page', async () => {
    const clientResponse = await fetchWorker(
      new Request(`${ORIGIN}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_name: 'Beginner MCP Client',
          redirect_uris: ['https://client.example/callback'],
          grant_types: ['authorization_code', 'refresh_token'],
          response_types: ['code'],
          token_endpoint_auth_method: 'none',
        }),
      }),
      env,
    );
    const client = await clientResponse.json();
    const authorizeUrl = new URL(`${ORIGIN}/authorize`);
    authorizeUrl.search = new URLSearchParams({
      response_type: 'code',
      client_id: client.client_id,
      redirect_uri: 'https://client.example/callback',
      state: 'state-123',
      scope: 'mcp:tools',
      code_challenge: await sha256Base64Url('a'.repeat(48)),
      code_challenge_method: 'S256',
      resource: MCP_URL,
    });

    const missingChallengeUrl = new URL(authorizeUrl);
    missingChallengeUrl.searchParams.delete('code_challenge');
    expect(
      (await fetchWorker(new Request(missingChallengeUrl), env)).status,
    ).toBe(400);

    const invalidResponseTypeUrl = new URL(authorizeUrl);
    invalidResponseTypeUrl.searchParams.set('response_type', 'unsupported');
    expect(
      (await fetchWorker(new Request(invalidResponseTypeUrl), env)).status,
    ).toBe(400);

    const invalidScopeUrl = new URL(authorizeUrl);
    invalidScopeUrl.searchParams.set('scope', 'admin');
    expect(
      (await fetchWorker(new Request(invalidScopeUrl), env)).status,
    ).toBe(400);

    const getResponse = await fetchWorker(new Request(authorizeUrl), env);
    const html = await getResponse.text();
    const csrf = extractCsrf(html);
    const cookie = extractCookie(getResponse);

    expect(getResponse.status).toBe(200);
    expect(getResponse.headers.get('Content-Type')).toContain('text/html');
    expect(html).toContain('Beginner MCP Client');
    expect(html).toContain('License Key');
    expect(csrf).toBeTruthy();
    expect(cookie).toBe(`mingli_oauth_csrf=${csrf}`);

    const rejected = await fetchWorker(
      new Request(`${ORIGIN}/authorize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          Cookie: 'mingli_oauth_csrf=wrong',
        },
        body: new URLSearchParams({ csrf, license_key: LICENSE_KEY }),
      }),
      env,
    );
    expect(rejected.status).toBe(403);
  });

  it('completes S256 PKCE OAuth and applies the license quota', async () => {
    const verifier = 'pkce-verifier-with-enough-entropy-12345678901234567890';
    const challenge = await sha256Base64Url(verifier);
    const registration = await fetchWorker(
      new Request(`${ORIGIN}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_name: 'ChatGPT',
          redirect_uris: ['https://client.example/callback'],
          grant_types: ['authorization_code', 'refresh_token'],
          response_types: ['code'],
          token_endpoint_auth_method: 'none',
        }),
      }),
      env,
    );
    expect(registration.status).toBe(201);
    const client = await registration.json();

    const authorizeUrl = new URL(`${ORIGIN}/authorize`);
    authorizeUrl.search = new URLSearchParams({
      response_type: 'code',
      client_id: client.client_id,
      redirect_uri: 'https://client.example/callback',
      state: 'oauth-state',
      scope: 'mcp:tools',
      code_challenge: challenge,
      code_challenge_method: 'S256',
      resource: MCP_URL,
    });
    const consent = await fetchWorker(new Request(authorizeUrl), env);
    const consentHtml = await consent.text();
    const csrf = extractCsrf(consentHtml);
    const cookie = extractCookie(consent);

    const approval = await fetchWorker(
      new Request(`${ORIGIN}/authorize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          Cookie: cookie,
        },
        body: new URLSearchParams({ csrf, license_key: LICENSE_KEY }),
        redirect: 'manual',
      }),
      env,
    );
    expect(approval.status).toBe(302);
    const callback = new URL(approval.headers.get('Location'));
    expect(callback.origin + callback.pathname).toBe('https://client.example/callback');
    expect(callback.searchParams.get('state')).toBe('oauth-state');
    const code = callback.searchParams.get('code');
    expect(code).toBeTruthy();

    const tokenResponse = await fetchWorker(
      new Request(`${ORIGIN}/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          grant_type: 'authorization_code',
          client_id: client.client_id,
          code,
          code_verifier: verifier,
          redirect_uri: 'https://client.example/callback',
          resource: MCP_URL,
        }),
      }),
      env,
    );
    expect(tokenResponse.status).toBe(200);
    const tokens = await tokenResponse.json();
    expect(tokens.token_type).toBe('bearer');
    expect(tokens.access_token).toBeTruthy();
    expect(tokens.refresh_token).toBeTruthy();
    for (const [key, value] of env.OAUTH_KV.entries) {
      expect(`${key}\n${value}`).not.toContain(LICENSE_KEY);
    }

    const toolResponse = await fetchWorker(
      mcpRequest('tools/call', `Bearer ${tokens.access_token}`),
      env,
    );
    expect(toolResponse.status).toBe(200);
    expect((await toolResponse.json()).authorization).toBe(`Bearer ${MASTER_KEY}`);

    const quotaKeys = [...env.LICENSES.entries.keys()].filter((key) =>
      key.startsWith(`mcpquota:${LICENSE_KEY}:`),
    );
    expect(quotaKeys).toHaveLength(1);
    expect(await env.LICENSES.get(quotaKeys[0])).toBe('1');
  });
});
