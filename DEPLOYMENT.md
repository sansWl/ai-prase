# AI-Prase 项目 Docker 部署指南

## 项目概述

AI-Prase 是一个基于 FastAPI 的 AI 应用服务，支持 LLM、Embedding、RAG 等功能。

## 前置要求

- Docker (版本 20.10+)
- Docker Compose (版本 2.0+)
- 至少 2GB 可用内存

## 快速开始

### 方式一：使用部署脚本（推荐）

```bash
# 给脚本添加执行权限
chmod +x docker-deploy.sh

# 一键部署
./docker-deploy.sh deploy

# 或者分步操作
./docker-deploy.sh build  # 构建镜像
./docker-deploy.sh start  # 启动容器
```

### 方式二：使用 Docker Compose

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方式三：使用 Docker 命令

```bash
# 构建镜像
docker build -t ai-prase:latest .

# 启动容器
docker run -d \
  --name ai-prase-container \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  ai-prase:latest
```

## 环境配置

### 必需的环境变量

创建 `.env` 文件并配置以下变量：

```env
# Web 服务器配置
WEB_SERVER_HOST=0.0.0.0
WEB_SERVER_PORT=8000

# Neo4j 配置（可选）
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=your_username
NEO4J_PASSWORD=your_password

# LLM 配置
LLM_TYPE=ollama  # 或 openai

# OpenAI 配置（如果使用 OpenAI）
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0

# Ollama 配置（如果使用 Ollama）
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:8b
OLLAMA_SYSTEM_PROMPT=你是一个遵循 ReAct 格式的智能助手

# Embedding 配置
EMBEDDING_TYPE=ollama  # 或 openai
OLLAMA_EMBEDDING_MODEL=embeddinggemma:300m
```

## 部署脚本命令说明

```bash
./docker-deploy.sh <command>

可用命令:
  build   - 构建 Docker 镜像
  start   - 启动容器
  stop    - 停止容器
  restart - 重启容器
  logs    - 查看容器日志
  status  - 查看容器状态
  clean   - 清理未使用的镜像和容器
  deploy  - 构建并部署（默认命令）
```

## 访问服务

部署成功后，可以通过以下地址访问服务：

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/heartbeat
- **配置接口**: http://localhost:8000/api/config/env/configs

## 常用操作

### 查看容器日志

```bash
docker logs -f ai-prase-container
```

### 进入容器内部

```bash
docker exec -it ai-prase-container /bin/bash
```

### 重启容器

```bash
docker restart ai-prase-container
```

### 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并部署
./docker-deploy.sh deploy
```

## 生产环境建议

### 1. 安全配置

- 使用 HTTPS
- 配置防火墙规则
- 定期更新依赖包
- 使用 secrets 管理敏感信息

### 2. 性能优化

- 调整容器资源限制
- 使用负载均衡
- 配置日志轮转
- 监控容器健康状态

### 3. 数据持久化

```yaml
# docker-compose.yml 中添加卷挂载
volumes:
  - ./data:/app/data
  - ./logs:/app/logs
```

### 4. 资源限制

```yaml
# docker-compose.yml 中添加资源限制
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
    reservations:
      cpus: '1'
      memory: 2G
```

## 故障排查

### 容器无法启动

1. 检查日志：`docker logs ai-prase-container`
2. 检查环境变量配置
3. 检查端口占用：`netstat -tlnp | grep 8000`

### 服务无响应

1. 检查容器状态：`docker ps`
2. 检查健康状态：`curl http://localhost:8000/heartbeat`
3. 检查资源使用：`docker stats ai-prase-container`

### 连接问题

1. 检查网络配置
2. 验证外部服务连接（Neo4j、Ollama 等）
3. 检查防火墙规则

## 监控和日志

### 日志管理

```bash
# 查看实时日志
docker logs -f --tail 100 ai-prase-container

# 导出日志
docker logs ai-prase-container > app.log 2>&1
```

### 健康检查

```bash
# 检查容器健康状态
docker inspect --format='{{.State.Health.Status}}' ai-prase-container

# 手动健康检查
curl -f http://localhost:8000/heartbeat
```

## 备份和恢复

### 备份

```bash
# 导出镜像
docker save ai-prase:latest | gzip > ai-prase-latest.tar.gz

# 备份配置
tar -czf config-backup.tar.gz .env docker-compose.yml
```

### 恢复

```bash
# 导入镜像
docker load < ai-prase-latest.tar.gz

# 恢复配置
tar -xzf config-backup.tar.gz
```

## 联系支持

如有问题，请查看项目文档或提交 Issue。
