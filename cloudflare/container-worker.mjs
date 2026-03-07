import { Container } from "@cloudflare/containers";

export class MingliContainer extends Container {
  defaultPort = 8080;
  requiredPorts = [8080];
  sleepAfter = "10m";
  enableInternet = true;
  pingEndpoint = "/health";
  envVars = {
    TRANSPORT_TYPE: "http",
    HTTP_HOST: "0.0.0.0",
    HTTP_PORT: "8080",
    LOG_LEVEL: "INFO",
    ENABLE_RATE_LIMIT: "true",
    RATE_LIMIT_REQUESTS: "100",
    RATE_LIMIT_WINDOW: "60",
  };
}

export default {
  async fetch(request, env) {
    const container = env.MINGLI_CONTAINER.getByName("mingli-http");
    await container.startAndWaitForPorts();
    return container.fetch(request);
  },
};
