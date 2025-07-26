#!/bin/bash

# Work Manager Backend 服务器部署脚本
# 适用于 Ubuntu/Debian 系统

set -e

echo "🚀 Work Manager Backend 服务器部署脚本"
echo "========================================"

# 检查是否为 root 用户
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  请不要使用 root 用户运行此脚本"
    echo "建议创建一个专用用户，例如："
    echo "sudo adduser workmanager"
    echo "sudo usermod -aG sudo workmanager"
    exit 1
fi

# 配置变量
APP_NAME="work_manager_backend"
APP_USER=$(whoami)
APP_DIR="/home/$APP_USER/$APP_NAME"
SERVICE_NAME="work-manager-backend"
PYTHON_VERSION="3.11"

echo "📋 部署配置："
echo "   应用名称: $APP_NAME"
echo "   用户: $APP_USER"
echo "   目录: $APP_DIR"
echo "   服务名: $SERVICE_NAME"
echo ""

# 更新系统
echo "🔄 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 安装必要的系统依赖
echo "📦 安装系统依赖..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    nginx \
    supervisor \
    curl \
    wget \
    unzip \
    build-essential \
    libmysqlclient-dev \
    pkg-config

# 检查 Python 版本
echo "🐍 检查 Python 版本..."
python3 --version

# 创建应用目录
echo "📁 创建应用目录..."
mkdir -p $APP_DIR
cd $APP_DIR

# 克隆代码（如果目录为空）
if [ ! -f "main.py" ]; then
    echo "📥 克隆代码仓库..."
    git clone https://github.com/neoo726/work_manager_backend.git .
else
    echo "📥 更新代码..."
    git pull origin main
fi

# 创建虚拟环境
echo "🔧 创建 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装 Python 依赖
echo "📦 安装 Python 依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建环境配置文件
echo "⚙️  创建环境配置..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请根据需要修改配置"
else
    echo "✅ .env 文件已存在"
fi

# 测试数据库连接
echo "🔍 测试数据库连接..."
python test_mysql_connection.py

echo ""
echo "✅ 基础部署完成！"
echo ""
echo "📝 接下来的步骤："
echo "1. 配置 Nginx 反向代理"
echo "2. 配置 Supervisor 进程管理"
echo "3. 启动服务"
echo ""
read -p "是否继续配置服务？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔧 继续配置服务..."
else
    echo "👋 部署脚本结束，请手动完成后续配置"
    exit 0
fi

# 配置 Supervisor
echo "🔧 配置 Supervisor..."
sudo tee /etc/supervisor/conf.d/$SERVICE_NAME.conf > /dev/null <<EOF
[program:$SERVICE_NAME]
command=$APP_DIR/venv/bin/python $APP_DIR/main.py
directory=$APP_DIR
user=$APP_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/$SERVICE_NAME.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3
environment=PATH="$APP_DIR/venv/bin"
EOF

# 配置 Nginx
echo "🔧 配置 Nginx..."
sudo tee /etc/nginx/sites-available/$SERVICE_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name localhost;  # 替换为您的域名

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # CORS 支持
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept, Authorization";
        
        if (\$request_method = 'OPTIONS') {
            return 204;
        }
    }
    
    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
    
    # API 文档
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
    }
}
EOF

# 启用 Nginx 站点
sudo ln -sf /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/
sudo nginx -t

# 重启服务
echo "🔄 启动服务..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start $SERVICE_NAME
sudo systemctl reload nginx

# 检查服务状态
echo "🔍 检查服务状态..."
sudo supervisorctl status $SERVICE_NAME
sudo systemctl status nginx --no-pager -l

echo ""
echo "🎉 部署完成！"
echo ""
echo "📊 服务信息："
echo "   应用目录: $APP_DIR"
echo "   服务状态: sudo supervisorctl status $SERVICE_NAME"
echo "   日志文件: /var/log/$SERVICE_NAME.log"
echo "   Nginx 配置: /etc/nginx/sites-available/$SERVICE_NAME"
echo ""
echo "🔗 访问地址："
echo "   API 服务: http://your-server-ip/"
echo "   API 文档: http://your-server-ip/docs"
echo "   健康检查: http://your-server-ip/health"
echo ""
echo "📝 管理命令："
echo "   查看日志: sudo tail -f /var/log/$SERVICE_NAME.log"
echo "   重启服务: sudo supervisorctl restart $SERVICE_NAME"
echo "   停止服务: sudo supervisorctl stop $SERVICE_NAME"
echo "   启动服务: sudo supervisorctl start $SERVICE_NAME"
echo ""
