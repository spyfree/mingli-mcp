# Cloudflare Containers 部署说明

## 目标

将 `mingli-mcp` 作为长期在线的 HTTPS MCP 服务部署到 Cloudflare Containers，
避免依赖本地机器常开。

## 当前实现

- Worker 入口：`cloudflare/container-worker.mjs`
- Wrangler 配置：`wrangler.jsonc`
- 容器镜像：复用仓库根目录 `Dockerfile`

当前采用低成本的单实例按需方案：

- `instance_type = "lite"`
- `max_instances = 1`
- `sleepAfter = "2m"`，空闲两分钟后自动停止
- 通过 `getByName("mingli-http")` 固定路由到同一个容器实例
- `/` 和 `/health` 直接在 Worker 边缘响应，未知路径在边缘返回 404，避免无效请求唤醒容器

新请求会自动重新启动已休眠的容器，因此休眠后的首次 MCP 请求可能有冷启动延迟。
后续如果确认无状态化需求更强，可以改成多实例负载均衡。

## 前置条件

1. 安装并登录 Wrangler
   - `npm install`
   - `npx wrangler login`
2. 确认账号可用
   - `npx wrangler whoami`
3. 如需绑定自定义域名，再到 Cloudflare Dashboard 配置 routes / 域名映射

## 本地验证

```bash
npm install
npx wrangler whoami
npx wrangler containers list
```

## 首次部署

```bash
npx wrangler deploy
```

部署成功后，Worker 会把请求转发到容器内运行的 Python HTTP 服务：

- 健康检查：`/health`
- MCP 入口：`/mcp`

## 注意事项

- 当前本机 `wrangler` 登录态已失效，需要重新登录。
- 旧的 `mcp.lee.locker` 方案属于 Cloudflare Tunnel，不适合本机会关机的长期托管场景。
- Cloudflare Containers 仍处于 beta，后续可能需要跟进平台配置变化。
