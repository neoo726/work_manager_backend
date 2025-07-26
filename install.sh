#!/bin/bash

# Work Manager Backend 一键安装脚本
# 可以直接在服务器上运行此脚本

set -e

echo "🚀 Work Manager Backend 一键安装"
echo "================================="
echo "此脚本将自动部署 Work Manager Backend 到您的服务器"
echo ""

# 检测系统
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ -f /etc/debian_version ]; then
        OS="debian"
        echo "🐧 检测到 Debian/Ubuntu 系统"
    elif [ -f /etc/redhat-release ]; then
        OS="redhat"
        echo "🐧 检测到 RedHat/CentOS 系统"
    else
        OS="linux"
        echo "🐧 检测到 Linux 系统"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "🍎 检测到 macOS 系统"
else
    OS="unknown"
    echo "❓ 未知系统类型: $OSTYPE"
fi

# 选择部署方式
echo ""
echo "请选择部署方式："
echo "1) 快速部署 (推荐，适合测试和开发)"
echo "2) Docker 部署 (推荐，适合生产环境)"
echo "3) 完整部署 (包含 Nginx 和 Supervisor)"
echo ""
read -p "请输入选择 (1-3): " -n 1 -r
echo ""

case $REPLY in
    1)
        DEPLOY_TYPE="quick"
        echo "✅ 选择快速部署"
        ;;
    2)
        DEPLOY_TYPE="docker"
        echo "✅ 选择 Docker 部署"
        ;;
    3)
        DEPLOY_TYPE="full"
        echo "✅ 选择完整部署"
        ;;
    *)
        echo "❌ 无效选择，默认使用快速部署"
        DEPLOY_TYPE="quick"
        ;;
esac

echo ""

# 设置变量
REPO_URL="https://github.com/neoo726/work_manager_backend.git"
APP_DIR="$HOME/work_manager_backend"
PORT=${PORT:-8000}

# 检查必要工具
echo "🔍 检查系统环境..."

# 检查 git
if ! command -v git &> /dev/null; then
    echo "📦 安装 git..."
    if [ "$OS" = "debian" ]; then
        sudo apt update && sudo apt install -y git
    elif [ "$OS" = "redhat" ]; then
        sudo yum install -y git
    elif [ "$OS" = "macos" ]; then
        echo "请先安装 Xcode Command Line Tools: xcode-select --install"
        exit 1
    else
        echo "❌ 请手动安装 git"
        exit 1
    fi
fi

# 检查 Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✅ 找到 Python: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version | cut -d' ' -f2)
    echo "✅ 找到 Python: $PYTHON_VERSION"
else
    echo "📦 安装 Python..."
    if [ "$OS" = "debian" ]; then
        sudo apt update && sudo apt install -y python3 python3-pip python3-venv
        PYTHON_CMD="python3"
    elif [ "$OS" = "redhat" ]; then
        sudo yum install -y python3 python3-pip
        PYTHON_CMD="python3"
    else
        echo "❌ 请手动安装 Python 3.8+"
        exit 1
    fi
fi

# Docker 部署特殊处理
if [ "$DEPLOY_TYPE" = "docker" ]; then
    if ! command -v docker &> /dev/null; then
        echo "📦 安装 Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        echo "⚠️  Docker 已安装，请重新登录后再次运行此脚本"
        exit 0
    else
        echo "✅ 找到 Docker: $(docker --version)"
    fi
fi

# 克隆代码
echo "📥 下载代码..."
if [ -d "$APP_DIR" ]; then
    echo "目录已存在，更新代码..."
    cd "$APP_DIR"
    git pull origin main
else
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi

# 根据部署类型执行相应脚本
case $DEPLOY_TYPE in
    "quick")
        echo "🚀 执行快速部署..."
        chmod +x quick_deploy.sh
        ./quick_deploy.sh
        ;;
    "docker")
        echo "🐳 执行 Docker 部署..."
        chmod +x docker_deploy.sh
        ./docker_deploy.sh
        ;;
    "full")
        echo "🔧 执行完整部署..."
        chmod +x deploy_to_server.sh
        ./deploy_to_server.sh
        ;;
esac

echo ""
echo "🎉 安装完成！"
echo ""
echo "📊 服务信息："
echo "   部署目录: $APP_DIR"
echo "   部署类型: $DEPLOY_TYPE"
echo "   服务端口: $PORT"
echo ""
echo "🔗 访问地址："
echo "   API 服务: http://$(hostname -I | awk '{print $1}'):$PORT"
echo "   API 文档: http://$(hostname -I | awk '{print $1}'):$PORT/docs"
echo "   健康检查: http://$(hostname -I | awk '{print $1}'):$PORT/health"
echo ""
echo "📝 管理命令："
case $DEPLOY_TYPE in
    "quick")
        echo "   查看状态: cd $APP_DIR && ./check_status.sh"
        echo "   查看日志: cd $APP_DIR && tail -f app.log"
        echo "   重启服务: cd $APP_DIR && ./stop_server.sh && ./start_background.sh"
        ;;
    "docker")
        echo "   查看状态: cd $APP_DIR && ./docker_status.sh"
        echo "   查看日志: cd $APP_DIR && ./docker_logs.sh"
        echo "   重启服务: cd $APP_DIR && ./docker_restart.sh"
        ;;
    "full")
        echo "   查看状态: sudo supervisorctl status work-manager-backend"
        echo "   查看日志: sudo tail -f /var/log/work-manager-backend.log"
        echo "   重启服务: sudo supervisorctl restart work-manager-backend"
        ;;
esac
echo ""
echo "💡 提示："
echo "   - 请确保防火墙开放端口 $PORT"
echo "   - 如需修改配置，请编辑 $APP_DIR/.env 文件"
echo "   - 详细文档请查看: $APP_DIR/DEPLOYMENT_GUIDE.md"
echo ""
