import { Container } from "@cloudflare/containers";

export class MingliContainer extends Container {
  defaultPort = 8080;
  sleepAfter = "10m";
  enableInternet = true;

  constructor(ctx, env) {
    super(ctx, env);
    this.envVars = {
      TRANSPORT_TYPE: "http",
      HTTP_HOST: "0.0.0.0",
      HTTP_PORT: "8080",
      LOG_LEVEL: env.LOG_LEVEL ?? "INFO",
      ENABLE_RATE_LIMIT: env.ENABLE_RATE_LIMIT ?? "true",
      RATE_LIMIT_REQUESTS: env.RATE_LIMIT_REQUESTS ?? "100",
      RATE_LIMIT_WINDOW: env.RATE_LIMIT_WINDOW ?? "60",
    };
    // 通过 `wrangler secret put HTTP_API_KEY` 配置后自动启用Bearer认证
    if (env.HTTP_API_KEY) {
      this.envVars.HTTP_API_KEY = env.HTTP_API_KEY;
    }
    if (env.CORS_ORIGINS) {
      this.envVars.CORS_ORIGINS = env.CORS_ORIGINS;
    }
  }
}

// ── License 网关 ─────────────────────────────────────────────────────
// mingli-paipan (../mingli_worker) 售卖 mcp_access 产品后，Creem webhook 把
// license 写进共享的 LICENSES KV（格式见其 functions/api/_lib/license.ts）。
// 这里校验 "Authorization: Bearer ML-XXXX-XXXX-XXXX-XXXX"，通过后把请求头
// 换成内部主密钥转发给容器；主密钥本身也照常放行。

const LICENSE_RE = /^ML(-[A-Z0-9]{4}){4}$/;
const MCP_PRODUCT_KEY = "mcp_access";
const QUOTA_TTL_SECONDS = 2 * 24 * 60 * 60;

function jsonError(status, code, message) {
  return new Response(
    JSON.stringify({ jsonrpc: "2.0", error: { code, message }, id: null }),
    { status, headers: { "Content-Type": "application/json" } },
  );
}

/**
 * 校验 /mcp 的授权。返回 null 表示原样转发（主密钥或无需处理），
 * 返回 Response 表示拒绝，返回 Request 表示已换头的新请求。
 */
async function authorizeMcpRequest(request, env) {
  const auth = request.headers.get("Authorization") || "";
  const token = auth.startsWith("Bearer ") ? auth.slice(7).trim() : "";
  const masterKey = env.HTTP_API_KEY || "";

  // 主密钥直通（容器内部会再校验一次）
  if (masterKey && token === masterKey) return null;

  const key = token.toUpperCase();
  if (!LICENSE_RE.test(key)) {
    return jsonError(401, -32001, "Missing or invalid license key");
  }
  if (!env.LICENSES) {
    return jsonError(500, -32603, "License store unavailable");
  }

  const stored = await env.LICENSES.get(`license:${key}`, { cacheTtl: 60 });
  if (!stored) {
    return jsonError(401, -32001, "Unknown license key");
  }

  let record;
  try {
    record = JSON.parse(stored);
  } catch {
    return jsonError(500, -32603, "Corrupt license record");
  }
  if (record.status !== "active" || record.productKey !== MCP_PRODUCT_KEY) {
    return jsonError(403, -32001, "License is not valid for MCP access");
  }

  // 每日配额：只对 tools/call 计数，initialize/tools/list 等不消耗。
  // KV 计数非原子，属软限制，防滥用足够。
  const bodyText = await request.text();
  let isToolCall = false;
  try {
    isToolCall = JSON.parse(bodyText)?.method === "tools/call";
  } catch {
    // 坏JSON照样转发，容器会回 -32700
  }

  if (isToolCall) {
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
  }

  const headers = new Headers(request.headers);
  if (masterKey) headers.set("Authorization", `Bearer ${masterKey}`);
  return new Request(request.url, { method: "POST", headers, body: bodyText });
}

export default {
  async fetch(request, env) {
    let forward = request;

    const url = new URL(request.url);
    if (url.pathname === "/mcp" && request.method === "POST") {
      const result = await authorizeMcpRequest(request, env);
      if (result instanceof Response) return result;
      if (result instanceof Request) forward = result;
    }

    const container = env.MINGLI_CONTAINER.getByName("mingli-http");
    await container.startAndWaitForPorts();
    return container.fetch(forward);
  },
};
