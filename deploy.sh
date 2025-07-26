#!/bin/bash

# Work Manager Backend 部署脚本

set -e

echo "🚀 Work Manager Backend 部署脚本"
echo "=================================="

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

echo "✅ Docker 环境检查通过"

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env 文件不存在，从示例文件创建..."
    cp .env.example .env
    echo "📝 请编辑 .env 文件配置数据库连接信息"
    echo "   特别是以下配置项："
    echo "   - DB_HOST=postgres"
    echo "   - DB_NAME=work_manager"
    echo "   - DB_USER=work_manager_user"
    echo "   - DB_PASSWORD=work_manager_password"
    echo ""
    read -p "配置完成后按回车继续..."
fi

echo "✅ 环境配置检查完成"

# 构建和启动服务
echo "🔨 构建 Docker 镜像..."
docker-compose build

echo "🚀 启动服务..."
docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 测试健康检查
echo "🏥 测试服务健康状态..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 服务启动成功！"
    echo ""
    echo "🎉 部署完成！"
    echo "📊 服务信息："
    echo "   - API 服务: http://localhost:8000"
    echo "   - API 文档: http://localhost:8000/docs"
    echo "   - 健康检查: http://localhost:8000/health"
    echo "   - 数据库: localhost:5432"
    echo ""
    echo "📝 管理命令："
    echo "   - 查看日志: docker-compose logs -f"
    echo "   - 停止服务: docker-compose down"
    echo "   - 重启服务: docker-compose restart"
    echo ""
else
    echo "❌ 服务启动失败，请检查日志："
    echo "   docker-compose logs"
fi
