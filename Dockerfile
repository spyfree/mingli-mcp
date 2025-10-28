FROM python:3.11-slim

WORKDIR /app

# 安装依赖
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
