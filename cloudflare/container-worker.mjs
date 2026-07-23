import { Container } from '@cloudflare/containers';
import { OAuthProvider } from '@cloudflare/workers-oauth-provider';

export class MingliContainer extends Container {
  defaultPort = 8080;
  sleepAfter = '10m';
  enableInternet = true;

  constructor(ctx, env) {
    super(ctx, env);
    this.envVars = {
      TRANSPORT_TYPE: 'http',
      HTTP_HOST: '0.0.0.0',
      HTTP_PORT: '8080',
      LOG_LEVEL: env.LOG_LEVEL ?? 'INFO',
      ENABLE_RATE_LIMIT: env.ENABLE_RATE_LIMIT ?? 'true',
      RATE_LIMIT_REQUESTS: env.RATE_LIMIT_REQUESTS ?? '100',
      RATE_LIMIT_WINDOW: env.RATE_LIMIT_WINDOW ?? '60',
    };
    // 通过 `wrangler secret put HTTP_API_KEY` 配置后自动启用 Bearer 认证。
    if (env.HTTP_API_KEY) {
      this.envVars.HTTP_API_KEY = env.HTTP_API_KEY;
    }
    if (env.CORS_ORIGINS) {
      this.envVars.CORS_ORIGINS = env.CORS_ORIGINS;
    }
  }
}

// ── License 与 OAuth 网关 ────────────────────────────────────────────
// mingli-paipan (../mingli_worker) 售卖 mcp_access 后，Creem webhook 把
// license 写进共享的 LICENSES KV。新客户端走标准 OAuth + PKCE，在授权页
// 输入 license 一次；老客户端仍可直接使用 Bearer ML-...。

const LICENSE_RE = /^ML(-[A-Z0-9]{4}){4}$/;
const MCP_PRODUCT_KEY = 'mcp_access';
const MCP_SCOPE = 'mcp:tools';
const QUOTA_TTL_SECONDS = 2 * 24 * 60 * 60;
const CONSENT_TTL_SECONDS = 10 * 60;
const PURCHASE_URL = 'https://lee.locker/mcp';
const CSRF_COOKIE = 'mingli_oauth_csrf';

// 握手、能力发现和静态资源不产生排盘算力成本。真正执行工具时才授权和计数。
const FREE_METHODS = new Set([
  'initialize',
  'ping',
  'tools/list',
  'prompts/list',
  'prompts/get',
  'resources/list',
  'resources/read',
  'resources/get',
  'resources/templates/list',
]);

function jsonError(status, code, message, headers = {}) {
  return new Response(
    JSON.stringify({
      jsonrpc: '2.0',
      error: { code, message, data: { purchaseUrl: PURCHASE_URL } },
      id: null,
    }),
    {
      status,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        ...headers,
      },
    },
  );
}

function oauthChallenge(request, description = 'A valid MCP authorization is required.') {
  const url = new URL(request.url);
  const resourceMetadata = `${url.origin}/.well-known/oauth-protected-resource${url.pathname}`;
  return [
    'Bearer realm="OAuth"',
    `resource_metadata="${resourceMetadata}"`,
    'error="invalid_token"',
    `error_description="${description}"`,
  ].join(', ');
}

function licenseRequiredError(request, detail) {
  return jsonError(
    401,
    -32001,
    `${detail} Get a license key at ${PURCHASE_URL}. ` +
      `需要 License Key，请前往 ${PURCHASE_URL} 购买。`,
    { 'WWW-Authenticate': oauthChallenge(request, detail) },
  );
}

async function readMcpMethod(request) {
  if (request.method !== 'POST') return null;
  try {
    return (await request.clone().json())?.method ?? null;
  } catch {
    return null;
  }
}

function isFreeMethod(method) {
  return (
    typeof method === 'string' &&
    (FREE_METHODS.has(method) || method.startsWith('notifications/'))
  );
}

async function validateLicenseKey(candidate, env) {
  const key = String(candidate || '').trim().toUpperCase();
  if (!LICENSE_RE.test(key) || !env.LICENSES) return null;

  const stored = await env.LICENSES.get(`license:${key}`, { cacheTtl: 60 });
  if (!stored) return null;

  let record;
  try {
    record = JSON.parse(stored);
  } catch {
    return null;
  }
  if (record.status !== 'active' || record.productKey !== MCP_PRODUCT_KEY) {
    return null;
  }
  return { key, record };
}

async function consumeQuota(key, env) {
  const day = new Date().toISOString().slice(0, 10);
  const quotaKey = `mcpquota:${key}:${day}`;
  const used = Number((await env.LICENSES.get(quotaKey)) || 0);
  const limit = Number(env.MCP_DAILY_QUOTA || 200);
  if (used >= limit) {
    return jsonError(429, -32029, `Daily MCP quota exceeded (${limit} tool calls/day)`);
  }
  await env.LICENSES.put(quotaKey, String(used + 1), {
    expirationTtl: QUOTA_TTL_SECONDS,
  });
  return null;
}

function withInternalAuthorization(request, env) {
  const headers = new Headers(request.headers);
  if (env.HTTP_API_KEY) {
    headers.set('Authorization', `Bearer ${env.HTTP_API_KEY}`);
  } else {
    headers.delete('Authorization');
  }
  return new Request(request, { headers });
}

async function forwardToContainer(request, env) {
  const container = env.MINGLI_CONTAINER.getByName('mingli-http');
  await container.startAndWaitForPorts();
  return container.fetch(request);
}

async function forwardAuthorizedToContainer(request, env) {
  return forwardToContainer(withInternalAuthorization(request, env), env);
}

async function authorizeAndForward(request, env, ctx) {
  const props = ctx.props || {};
  const method = await readMcpMethod(request);

  if (props.authKind === 'master') {
    return forwardAuthorizedToContainer(request, env);
  }

  const validated = await validateLicenseKey(props.licenseKey, env);
  if (!validated) {
    return licenseRequiredError(request, 'This license is no longer active for MCP access.');
  }
  if (method === 'tools/call') {
    const quotaError = await consumeQuota(validated.key, env);
    if (quotaError) return quotaError;
  }
  return forwardAuthorizedToContainer(request, env);
}

async function resolveExternalToken({ token, env }) {
  if (env.HTTP_API_KEY && token === env.HTTP_API_KEY) {
    return { props: { authKind: 'master' } };
  }

  const validated = await validateLicenseKey(token, env);
  if (!validated) return null;
  return {
    props: {
      authKind: 'license',
      licenseKey: validated.key,
    },
  };
}

function parseCookies(request) {
  const values = {};
  for (const pair of (request.headers.get('Cookie') || '').split(';')) {
    const separator = pair.indexOf('=');
    if (separator === -1) continue;
    const key = pair.slice(0, separator).trim();
    const value = pair.slice(separator + 1).trim();
    if (key) values[key] = value;
  }
  return values;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function consentHeaders(csrf, clearCookie = false) {
  const cookie = clearCookie
    ? `${CSRF_COOKIE}=; Path=/authorize; Max-Age=0; HttpOnly; Secure; SameSite=Lax`
    : `${CSRF_COOKIE}=${csrf}; Path=/authorize; Max-Age=${CONSENT_TTL_SECONDS}; ` +
      'HttpOnly; Secure; SameSite=Lax';
  return {
    'Content-Type': 'text/html; charset=utf-8',
    'Cache-Control': 'no-store',
    'Content-Security-Policy':
      "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; " +
      "base-uri 'none'; frame-ancestors 'none'",
    'Referrer-Policy': 'no-referrer',
    'X-Content-Type-Options': 'nosniff',
    'Set-Cookie': cookie,
  };
}

function renderConsentPage({ csrf, clientName, clientUri, error = '' }, status = 200) {
  const safeClientName = escapeHtml(clientName || 'MCP Client');
  const safeClientUri = clientUri ? escapeHtml(clientUri) : '';
  const errorMarkup = error
    ? `<div class="error" role="alert">${escapeHtml(error)}</div>`
    : '';
  const clientUriMarkup = safeClientUri
    ? `<p class="client-uri">${safeClientUri}</p>`
    : '';

  return new Response(
    `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>连接命理 MCP</title>
  <style>
    :root { color-scheme: light; font-family: ui-sans-serif, system-ui, -apple-system, sans-serif; }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 24px;
      color: #352617; background: linear-gradient(145deg, #fbf8ef, #f3ead4); }
    main { width: min(100%, 480px); background: rgba(255,255,255,.92); border: 1px solid #dbc99d;
      border-radius: 24px; padding: 28px; box-shadow: 0 18px 50px rgba(70,48,16,.12); }
    .mark { width: 48px; height: 48px; display: grid; place-items: center; border-radius: 14px;
      color: #fff; background: #8d241f; font-size: 24px; }
    h1 { margin: 20px 0 8px; font-size: 28px; }
    .intro { color: #6c5a43; line-height: 1.65; }
    .client { margin: 22px 0; padding: 16px; border-radius: 14px; background: #f8f3e6; }
    .client strong { display: block; font-size: 17px; overflow-wrap: anywhere; }
    .client-uri { margin: 5px 0 0; color: #806f58; font-size: 13px; overflow-wrap: anywhere; }
    label { display: block; margin-bottom: 8px; font-weight: 650; }
    input { width: 100%; min-height: 52px; padding: 0 14px; border: 1px solid #b8a67c;
      border-radius: 12px; background: #fff; color: #2e2418; font: inherit; text-transform: uppercase; }
    input:focus { outline: 3px solid rgba(176,129,25,.22); border-color: #a57614; }
    .hint { margin: 8px 0 18px; color: #77664e; font-size: 13px; line-height: 1.5; }
    .error { margin: 0 0 16px; padding: 12px; border-radius: 10px; color: #8d1e1a;
      background: #fff0ee; border: 1px solid #e7aaa4; }
    .actions { display: grid; grid-template-columns: 1fr 2fr; gap: 10px; }
    button { min-height: 50px; border-radius: 12px; border: 0; font: inherit; font-weight: 700;
      cursor: pointer; }
    .cancel { color: #5c4b34; background: #eee7d8; }
    .connect { color: white; background: #8d241f; }
    .privacy { margin: 18px 0 0; color: #85745d; font-size: 12px; line-height: 1.5; }
    @media (max-width: 420px) { main { padding: 22px; } .actions { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <main>
    <div class="mark">命</div>
    <h1>连接命理 MCP</h1>
    <p class="intro">授权后，你可以直接在支持 MCP 的 AI 客户端里调用专业紫微斗数与八字工具。</p>
    <div class="client">
      <span>正在连接</span>
      <strong>${safeClientName}</strong>
      ${clientUriMarkup}
    </div>
    ${errorMarkup}
    <form method="post" action="/authorize">
      <input type="hidden" name="csrf" value="${escapeHtml(csrf)}">
      <label for="license_key">License Key</label>
      <input id="license_key" name="license_key" type="text"
        placeholder="ML-XXXX-XXXX-XXXX-XXXX" autocomplete="one-time-code"
        autocapitalize="characters" spellcheck="false" required>
      <p class="hint">输入购买后获得的 Key。只需在授权时验证，不会显示给正在连接的客户端。</p>
      <div class="actions">
        <button class="cancel" name="decision" value="deny" type="submit" formnovalidate>取消</button>
        <button class="connect" name="decision" value="approve" type="submit">验证并连接</button>
      </div>
    </form>
    <p class="privacy">授权范围仅包括调用命理 MCP 工具。你可以随时在客户端中断开连接。</p>
  </main>
</body>
</html>`,
    { status, headers: consentHeaders(csrf) },
  );
}

async function hashLicenseSubject(key) {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(key));
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}

async function beginAuthorization(request, env) {
  try {
    const oauthRequest = await env.OAUTH_PROVIDER.parseAuthRequest(request);
    if (oauthRequest.responseType !== 'code') {
      throw new Error('Only the authorization code flow is supported.');
    }
    if (!oauthRequest.codeChallenge || oauthRequest.codeChallengeMethod !== 'S256') {
      throw new Error('S256 PKCE with a code challenge is required.');
    }
    if (oauthRequest.scope.some((scope) => scope !== MCP_SCOPE)) {
      throw new Error(`Unsupported OAuth scope. Supported scope: ${MCP_SCOPE}.`);
    }
    const client = await env.OAUTH_PROVIDER.lookupClient(oauthRequest.clientId);
    if (!client) return new Response('Unknown OAuth client', { status: 400 });

    const csrf = crypto.randomUUID();
    await env.OAUTH_KV.put(
      `consent:${csrf}`,
      JSON.stringify({
        request: oauthRequest,
        clientName: client.clientName || 'MCP Client',
        clientUri: client.clientUri || '',
      }),
      { expirationTtl: CONSENT_TTL_SECONDS },
    );
    return renderConsentPage({
      csrf,
      clientName: client.clientName,
      clientUri: client.clientUri,
    });
  } catch (error) {
    return new Response(`Invalid authorization request: ${error.message}`, {
      status: 400,
      headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' },
    });
  }
}

function redirectDenied(consent) {
  const redirect = new URL(consent.request.redirectUri);
  redirect.searchParams.set('error', 'access_denied');
  redirect.searchParams.set('error_description', 'The user declined authorization.');
  if (consent.request.state) redirect.searchParams.set('state', consent.request.state);
  return new Response(null, {
    status: 302,
    headers: {
      Location: redirect.toString(),
      ...consentHeaders('', true),
    },
  });
}

async function finishAuthorization(request, env) {
  const form = await request.formData();
  const csrf = String(form.get('csrf') || '');
  const cookieCsrf = parseCookies(request)[CSRF_COOKIE] || '';
  if (!csrf || csrf !== cookieCsrf) {
    return new Response('Authorization session validation failed. Please restart the connection.', {
      status: 403,
      headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' },
    });
  }

  const consent = await env.OAUTH_KV.get(`consent:${csrf}`, { type: 'json' });
  if (!consent) {
    return new Response('Authorization session expired. Please restart the connection.', {
      status: 400,
      headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' },
    });
  }

  if (form.get('decision') === 'deny') {
    await env.OAUTH_KV.delete(`consent:${csrf}`);
    return redirectDenied(consent);
  }

  const validated = await validateLicenseKey(form.get('license_key'), env);
  if (!validated) {
    return renderConsentPage(
      {
        csrf,
        clientName: consent.clientName,
        clientUri: consent.clientUri,
        error: 'Key 无效、已停用，或不包含 MCP 权限，请检查后重试。',
      },
      401,
    );
  }

  const userId = `license-${await hashLicenseSubject(validated.key)}`;
  const { redirectTo } = await env.OAUTH_PROVIDER.completeAuthorization({
    request: consent.request,
    userId,
    metadata: {
      productKey: MCP_PRODUCT_KEY,
      licenseSuffix: validated.key.slice(-4),
      clientName: consent.clientName,
    },
    scope: consent.request.scope.length ? consent.request.scope : [MCP_SCOPE],
    props: {
      authKind: 'license',
      licenseKey: validated.key,
    },
  });
  await env.OAUTH_KV.delete(`consent:${csrf}`);
  return new Response(null, {
    status: 302,
    headers: {
      Location: redirectTo,
      ...consentHeaders('', true),
    },
  });
}

const defaultHandler = {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/authorize') {
      if (request.method === 'GET') return beginAuthorization(request, env);
      if (request.method === 'POST') return finishAuthorization(request, env);
      return new Response('Method not allowed', { status: 405, headers: { Allow: 'GET, POST' } });
    }
    return forwardToContainer(request, env);
  },
};

const apiHandler = {
  fetch: authorizeAndForward,
};

const oauthProvider = new OAuthProvider({
  apiRoute: '/mcp',
  apiHandler,
  defaultHandler,
  authorizeEndpoint: '/authorize',
  tokenEndpoint: '/token',
  clientRegistrationEndpoint: '/register',
  scopesSupported: [MCP_SCOPE],
  allowPlainPKCE: false,
  allowImplicitFlow: false,
  disallowPublicClientRegistration: false,
  clientIdMetadataDocumentEnabled: true,
  accessTokenTTL: 60 * 60,
  refreshTokenTTL: 30 * 24 * 60 * 60,
  resourceMetadata: {
    resource: 'https://mcp.lee.locker/mcp',
    authorization_servers: ['https://mcp.lee.locker'],
    scopes_supported: [MCP_SCOPE],
    bearer_methods_supported: ['header'],
    resource_name: 'Mingli MCP',
  },
  resolveExternalToken,
});

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === '/mcp' && isFreeMethod(await readMcpMethod(request))) {
      return forwardAuthorizedToContainer(request, env);
    }
    return oauthProvider.fetch(request, env, ctx);
  },

  scheduled(event, env, ctx) {
    ctx.waitUntil(oauthProvider.purgeExpiredData(env, { batchSize: 100 }));
  },
};
