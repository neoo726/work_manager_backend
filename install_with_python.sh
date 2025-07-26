#!/bin/bash

# Work Manager Backend 完整安装脚本（包含 Python 环境）
# 适用于没有 Python 环境的服务器

set -e

echo "🚀 Work Manager Backend 完整安装脚本"
echo "包含 Python 3.12.2 环境安装"
echo "======================================="

# 检测系统类型
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    echo "❌ 无法检测系统类型"
    exit 1
fi

echo "🐧 检测到系统: $OS $VERSION"

# 配置变量
PYTHON_VERSION="3.12.2"
APP_NAME="work_manager_backend"
APP_DIR="$HOME/$APP_NAME"
REPO_URL="https://github.com/neoo726/work_manager_backend.git"

echo "📋 安装配置："
echo "   Python 版本: $PYTHON_VERSION"
echo "   应用目录: $APP_DIR"
echo "   系统用户: $(whoami)"
echo ""

# 安装 Python 3.12
install_python_ubuntu() {
    echo "📦 在 Ubuntu/Debian 上安装 Python 3.12..."
    
    # 更新系统
    sudo apt update && sudo apt upgrade -y
    
    # 安装必要依赖
    sudo apt install -y software-properties-common curl wget git build-essential \
        libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
        libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
        libffi-dev liblzma-dev libmysqlclient-dev pkg-config
    
    # 添加 deadsnakes PPA
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    
    # 安装 Python 3.12
    sudo apt install -y python3.12 python3.12-venv python3.12-dev python3.12-distutils
    
    # 安装 pip
    curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.12
    
    # 创建符号链接
    sudo ln -sf /usr/bin/python3.12 /usr/local/bin/python3
    sudo ln -sf /usr/bin/python3.12 /usr/local/bin/python
    
    PYTHON_CMD="python3.12"
}

install_python_centos() {
    echo "📦 在 CentOS/RHEL 上安装 Python 3.12..."
    
    # 安装开发工具
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y openssl-devel bzip2-devel libffi-devel zlib-devel \
        sqlite-devel readline-devel tk-devel gdbm-devel db4-devel \
        libpcap-devel xz-devel expat-devel mysql-devel git curl wget
    
    # 下载并编译 Python 3.12.2
    cd /tmp
    wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
    tar xzf Python-$PYTHON_VERSION.tgz
    cd Python-$PYTHON_VERSION
    
    # 配置和编译
    ./configure --enable-optimizations --prefix=/usr/local
    make -j $(nproc)
    sudo make altinstall
    
    # 创建符号链接
    sudo ln -sf /usr/local/bin/python3.12 /usr/local/bin/python3
    sudo ln -sf /usr/local/bin/python3.12 /usr/local/bin/python
    sudo ln -sf /usr/local/bin/pip3.12 /usr/local/bin/pip3
    sudo ln -sf /usr/local/bin/pip3.12 /usr/local/bin/pip
    
    PYTHON_CMD="/usr/local/bin/python3.12"
    
    # 清理
    cd $HOME
    rm -rf /tmp/Python-$PYTHON_VERSION*
}

# 根据系统类型安装 Python
case $OS in
    ubuntu|debian)
        install_python_ubuntu
        ;;
    centos|rhel|rocky|almalinux)
        install_python_centos
        ;;
    *)
        echo "❌ 不支持的系统类型: $OS"
        echo "请手动安装 Python 3.12.2"
        exit 1
        ;;
esac

# 验证 Python 安装
echo "🔍 验证 Python 安装..."
$PYTHON_CMD --version
$PYTHON_CMD -m pip --version

if [ $? -eq 0 ]; then
    echo "✅ Python 安装成功"
else
    echo "❌ Python 安装失败"
    exit 1
fi

# 克隆项目代码
echo "📥 下载项目代码..."
if [ -d "$APP_DIR" ]; then
    echo "目录已存在，更新代码..."
    cd "$APP_DIR"
    git pull origin main
else
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi

# 创建虚拟环境
echo "🔧 创建 Python 虚拟环境..."
$PYTHON_CMD -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
echo "📦 升级 pip..."
pip install --upgrade pip

# 安装项目依赖
echo "📦 安装项目依赖..."
pip install -r requirements.txt

# 创建环境配置
echo "⚙️  创建环境配置..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ 已创建 .env 文件（MySQL 配置已预设）"
fi

# 测试数据库连接
echo "🔍 测试数据库连接..."
python test_mysql_connection.py

# 创建启动脚本
echo "📝 创建服务管理脚本..."

# 启动脚本
cat > start_service.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

echo "🚀 启动 Work Manager Backend..."
echo "时间: $(date)"
echo "Python: $(python --version)"
echo "目录: $(pwd)"
echo "================================="

python main.py
EOF

# 后台启动脚本
cat > start_background.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

# 检查是否已经在运行
if [ -f "app.pid" ]; then
    PID=$(cat app.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  服务已在运行 (PID: $PID)"
        echo "如需重启，请先运行: ./stop_service.sh"
        exit 1
    else
        rm -f app.pid
    fi
fi

echo "🚀 后台启动 Work Manager Backend..."
echo "Python: $(python --version)"
nohup python main.py > app.log 2>&1 &
echo $! > app.pid
echo "✅ 服务已启动 (PID: $(cat app.pid))"
echo "📊 查看日志: tail -f app.log"
echo "🛑 停止服务: ./stop_service.sh"
EOF

# 停止脚本
cat > stop_service.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

if [ -f "app.pid" ]; then
    PID=$(cat app.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "🛑 停止服务 (PID: $PID)..."
        kill $PID
        sleep 3
        if ps -p $PID > /dev/null 2>&1; then
            echo "强制停止..."
            kill -9 $PID
        fi
        rm -f app.pid
        echo "✅ 服务已停止"
    else
        echo "⚠️  服务未运行"
        rm -f app.pid
    fi
else
    echo "⚠️  未找到 PID 文件，尝试查找进程..."
    pkill -f "python.*main.py"
    echo "✅ 已尝试停止相关进程"
fi
EOF

# 状态检查脚本
cat > check_service.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

echo "📊 Work Manager Backend 服务状态"
echo "================================="
echo "Python: $(python --version)"
echo "目录: $(pwd)"
echo ""

# 检查进程
if [ -f "app.pid" ]; then
    PID=$(cat app.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ 服务运行中 (PID: $PID)"
        
        # 检查端口
        if netstat -tuln 2>/dev/null | grep ":8000 " > /dev/null; then
            echo "✅ 端口 8000 正在监听"
        else
            echo "⚠️  端口 8000 未监听"
        fi
        
        # 检查健康状态
        if command -v curl &> /dev/null; then
            echo "🔍 检查健康状态..."
            if curl -s http://localhost:8000/health > /dev/null; then
                echo "✅ 健康检查通过"
                curl -s http://localhost:8000/health | python -m json.tool
            else
                echo "❌ 健康检查失败"
            fi
        fi
    else
        echo "❌ 服务未运行"
        rm -f app.pid
    fi
else
    echo "❌ 服务未运行 (无 PID 文件)"
fi

echo ""
echo "📝 管理命令："
echo "   启动服务: ./start_background.sh"
echo "   停止服务: ./stop_service.sh"
echo "   查看日志: tail -f app.log"
echo "   前台运行: ./start_service.sh"
EOF

# 设置脚本权限
chmod +x *.sh

# 配置防火墙（如果需要）
echo "🔒 配置防火墙..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 8000
    echo "✅ UFW 防火墙已配置"
elif command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-port=8000/tcp
    sudo firewall-cmd --reload
    echo "✅ FirewallD 已配置"
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "📊 安装信息："
echo "   Python 版本: $($PYTHON_CMD --version)"
echo "   应用目录: $APP_DIR"
echo "   虚拟环境: $APP_DIR/venv"
echo ""
echo "🚀 启动服务："
echo "   前台运行: ./start_service.sh"
echo "   后台运行: ./start_background.sh"
echo ""
echo "📊 管理命令："
echo "   检查状态: ./check_service.sh"
echo "   停止服务: ./stop_service.sh"
echo "   查看日志: tail -f app.log"
echo ""
echo "🔗 访问地址："
SERVER_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "your-server-ip")
echo "   API 服务: http://$SERVER_IP:8000"
echo "   API 文档: http://$SERVER_IP:8000/docs"
echo "   健康检查: http://$SERVER_IP:8000/health"
echo ""
echo "💡 提示："
echo "   1. 服务使用虚拟环境，请确保使用提供的脚本管理"
echo "   2. 如需修改配置，请编辑 .env 文件"
echo "   3. 建议使用 screen 或 tmux 保持长期运行"
echo ""

# 询问是否立即启动
read -p "是否现在启动服务？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 启动服务..."
    ./start_background.sh
    sleep 3
    ./check_service.sh
fi

echo ""
echo "✅ 安装和配置完成！"
