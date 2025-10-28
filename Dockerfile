FROM python:3.11-slim

WORKDIR /app

# 安装 Node.js 和 npm（pythonmonkey 构建依赖）
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 安装包
RUN pip install --no-cache-dir -e .

# 暴露端口（如果使用HTTP模式）
EXPOSE 8080

# 设置环境变量
ENV TRANSPORT_TYPE=http
ENV HTTP_HOST=0.0.0.0
ENV HTTP_PORT=8080
ENV LOG_LEVEL=INFO

# 启动服务
CMD ["mingli-mcp"]
