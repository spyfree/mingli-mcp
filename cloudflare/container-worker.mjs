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

export default {
  async fetch(request, env) {
    const container = env.MINGLI_CONTAINER.getByName("mingli-http");
    await container.startAndWaitForPorts();
    return container.fetch(request);
  },
};
