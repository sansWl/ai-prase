#!/bin/bash

IMAGE_NAME="ai-prase"
IMAGE_TAG="latest"
CONTAINER_NAME="ai-prase-container"
PORT=8000

echo "========================================="
echo "构建 Docker 镜像"
echo "========================================="

docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

if [ $? -ne 0 ]; then
    echo "错误: Docker 镜像构建失败"
    exit 1
fi

echo ""
echo "========================================="
echo "停止并删除旧容器（如果存在）"
echo "========================================="

docker stop ${CONTAINER_NAME} 2>/dev/null || true
docker rm ${CONTAINER_NAME} 2>/dev/null || true

echo ""
echo "========================================="
echo "启动新容器"
echo "========================================="

docker run -d \
    --name ${CONTAINER_NAME} \
    -p ${PORT}:8000 \
    --env-file .env \
    --restart unless-stopped \
    ${IMAGE_NAME}:${IMAGE_TAG}

if [ $? -ne 0 ]; then
    echo "错误: 容器启动失败"
    exit 1
fi

echo ""
echo "========================================="
echo "部署成功！"
echo "========================================="
echo "容器名称: ${CONTAINER_NAME}"
echo "访问地址: http://localhost:${PORT}"
echo ""
echo "查看日志: docker logs -f ${CONTAINER_NAME}"
echo "停止容器: docker stop ${CONTAINER_NAME}"
echo "删除容器: docker rm ${CONTAINER_NAME}"
echo "========================================="
