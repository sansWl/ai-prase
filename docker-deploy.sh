#!/bin/bash

IMAGE_NAME="ai-prase"
IMAGE_TAG="${1:-latest}"
CONTAINER_NAME="ai-prase-container"
PORT=8000

build() {
    echo "构建 Docker 镜像: ${IMAGE_NAME}:${IMAGE_TAG}"
    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
    
    if [ $? -eq 0 ]; then
        echo "✓ 镜像构建成功"
    else
        echo "✗ 镜像构建失败"
        exit 1
    fi
}

start() {
    echo "启动容器: ${CONTAINER_NAME}"
    
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    docker rm ${CONTAINER_NAME} 2>/dev/null || true
    
    docker run -d \
        --name ${CONTAINER_NAME} \
        -p ${PORT}:8000 \
        --env-file .env \
        --restart unless-stopped \
        ${IMAGE_NAME}:${IMAGE_TAG}
    
    if [ $? -eq 0 ]; then
        echo "✓ 容器启动成功"
        echo "访问地址: http://localhost:${PORT}"
    else
        echo "✗ 容器启动失败"
        exit 1
    fi
}

stop() {
    echo "停止容器: ${CONTAINER_NAME}"
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    echo "✓ 容器已停止"
}

logs() {
    echo "查看容器日志: ${CONTAINER_NAME}"
    docker logs -f ${CONTAINER_NAME}
}

status() {
    echo "容器状态:"
    docker ps -a --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

clean() {
    echo "清理未使用的镜像和容器..."
    docker system prune -f
    echo "✓ 清理完成"
}

case "$1" in
    build)
        build
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        start
        ;;
    logs)
        logs
        ;;
    status)
        status
        ;;
    clean)
        clean
        ;;
    deploy)
        build
        start
        ;;
    *)
        echo "用法: $0 {build|start|stop|restart|logs|status|clean|deploy}"
        echo ""
        echo "命令说明:"
        echo "  build   - 构建 Docker 镜像"
        echo "  start   - 启动容器"
        echo "  stop    - 停止容器"
        echo "  restart - 重启容器"
        echo "  logs    - 查看容器日志"
        echo "  status  - 查看容器状态"
        echo "  clean   - 清理未使用的镜像和容器"
        echo "  deploy  - 构建并部署（默认命令）"
        exit 1
        ;;
esac
