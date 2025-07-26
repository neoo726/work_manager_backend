#!/bin/bash

# Work Manager Backend Docker 部署脚本

set -e

echo "🐳 Work Manager Backend Docker 部署"
echo "===================================="

# 配置变量
APP_NAME="work_manager_backend"
CONTAINER_NAME="work-manager-backend"
IMAGE_NAME="work-manager-backend:latest"
PORT=${PORT:-8000}
HOST_PORT=${HOST_PORT:-8000}

echo "📋 部署配置："
echo "   应用名称: $APP_NAME"
echo "   容器名称: $CONTAINER_NAME"
echo "   镜像名称: $IMAGE_NAME"
echo "   容器端口: $PORT"
echo "   主机端口: $HOST_PORT"
echo ""

# 检查 Docker
echo "🔍 检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    echo "安装命令："
    echo "curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "sudo sh get-docker.sh"
    exit 1
fi

echo "✅ Docker 版本: $(docker --version)"

# 创建工作目录
WORK_DIR="$HOME/$APP_NAME"
mkdir -p $WORK_DIR
cd $WORK_DIR

# 克隆或更新代码
if [ ! -f "main.py" ]; then
    echo "📥 克隆代码仓库..."
    git clone https://github.com/neoo726/work_manager_backend.git .
else
    echo "📥 更新代码..."
    git pull origin main
fi

# 创建生产环境 Dockerfile
echo "📝 创建生产环境 Dockerfile..."
cat > Dockerfile.prod << 'EOF'
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["python", "main.py"]
EOF

# 创建 .dockerignore
echo "📝 创建 .dockerignore..."
cat > .dockerignore << 'EOF'
.git
.gitignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
venv/
env/
ENV/
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
logs/
temp/
tmp/
docs/
*.md
!README.md
tests/
test_*.py
*_test.py
EOF

# 创建环境配置
if [ ! -f ".env" ]; then
    echo "⚙️  创建环境配置..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请根据需要修改"
fi

# 停止并删除现有容器
echo "🛑 停止现有容器..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# 构建镜像
echo "🔨 构建 Docker 镜像..."
docker build -f Dockerfile.prod -t $IMAGE_NAME .

# 运行容器
echo "🚀 启动容器..."
docker run -d \
    --name $CONTAINER_NAME \
    --restart unless-stopped \
    -p $HOST_PORT:$PORT \
    --env-file .env \
    -v $(pwd)/logs:/app/logs \
    $IMAGE_NAME

# 等待容器启动
echo "⏳ 等待容器启动..."
sleep 10

# 检查容器状态
echo "🔍 检查容器状态..."
docker ps | grep $CONTAINER_NAME

# 检查健康状态
echo "🏥 检查服务健康状态..."
if curl -f http://localhost:$HOST_PORT/health > /dev/null 2>&1; then
    echo "✅ 服务健康检查通过"
else
    echo "❌ 服务健康检查失败，查看日志："
    docker logs $CONTAINER_NAME
fi

# 创建管理脚本
echo "📝 创建管理脚本..."

# 启动脚本
cat > docker_start.sh << EOF
#!/bin/bash
echo "🚀 启动 Work Manager Backend 容器..."
docker start $CONTAINER_NAME
docker ps | grep $CONTAINER_NAME
EOF
chmod +x docker_start.sh

# 停止脚本
cat > docker_stop.sh << EOF
#!/bin/bash
echo "🛑 停止 Work Manager Backend 容器..."
docker stop $CONTAINER_NAME
EOF
chmod +x docker_stop.sh

# 重启脚本
cat > docker_restart.sh << EOF
#!/bin/bash
echo "🔄 重启 Work Manager Backend 容器..."
docker restart $CONTAINER_NAME
sleep 5
docker ps | grep $CONTAINER_NAME
EOF
chmod +x docker_restart.sh

# 日志查看脚本
cat > docker_logs.sh << EOF
#!/bin/bash
echo "📋 查看 Work Manager Backend 日志..."
docker logs -f $CONTAINER_NAME
EOF
chmod +x docker_logs.sh

# 状态检查脚本
cat > docker_status.sh << EOF
#!/bin/bash
echo "📊 Work Manager Backend 容器状态"
echo "================================="
echo "容器状态:"
docker ps -a | grep $CONTAINER_NAME
echo ""
echo "资源使用:"
docker stats --no-stream $CONTAINER_NAME 2>/dev/null || echo "容器未运行"
echo ""
echo "健康检查:"
if curl -s http://localhost:$HOST_PORT/health > /dev/null; then
    echo "✅ 服务正常"
else
    echo "❌ 服务异常"
fi
EOF
chmod +x docker_status.sh

echo ""
echo "🎉 Docker 部署完成！"
echo ""
echo "📊 容器信息："
echo "   容器名称: $CONTAINER_NAME"
echo "   镜像名称: $IMAGE_NAME"
echo "   端口映射: $HOST_PORT:$PORT"
echo ""
echo "🔗 访问地址："
echo "   API 服务: http://your-server-ip:$HOST_PORT"
echo "   API 文档: http://your-server-ip:$HOST_PORT/docs"
echo "   健康检查: http://your-server-ip:$HOST_PORT/health"
echo ""
echo "📝 管理命令："
echo "   查看状态: ./docker_status.sh"
echo "   查看日志: ./docker_logs.sh"
echo "   启动容器: ./docker_start.sh"
echo "   停止容器: ./docker_stop.sh"
echo "   重启容器: ./docker_restart.sh"
echo ""
echo "🐳 Docker 命令："
echo "   查看容器: docker ps"
echo "   查看日志: docker logs $CONTAINER_NAME"
echo "   进入容器: docker exec -it $CONTAINER_NAME bash"
echo "   删除容器: docker rm $CONTAINER_NAME"
echo "   删除镜像: docker rmi $IMAGE_NAME"
echo ""
