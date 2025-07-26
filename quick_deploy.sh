#!/bin/bash

# Work Manager Backend 快速部署脚本
# 适用于已有 Python 环境的服务器

set -e

echo "⚡ Work Manager Backend 快速部署"
echo "================================="

# 配置变量
APP_NAME="work_manager_backend"
APP_DIR="$HOME/$APP_NAME"
PORT=${PORT:-8000}

echo "📋 部署配置："
echo "   应用目录: $APP_DIR"
echo "   运行端口: $PORT"
echo "   用户: $(whoami)"
echo ""

# 创建应用目录
echo "📁 准备应用目录..."
mkdir -p $APP_DIR
cd $APP_DIR

# 克隆或更新代码
if [ ! -f "main.py" ]; then
    echo "📥 克隆代码仓库..."
    git clone https://github.com/neoo726/work_manager_backend.git .
else
    echo "📥 更新代码..."
    git pull origin main
fi

# 检查 Python
echo "🐍 检查 Python 环境..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ 未找到 Python，请先安装 Python 3.8+"
    exit 1
fi

echo "使用 Python: $($PYTHON_CMD --version)"

# 安装依赖
echo "📦 安装依赖..."
$PYTHON_CMD -m pip install --user -r requirements.txt

# 创建环境配置
echo "⚙️  配置环境..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ 已创建 .env 文件"
fi

# 测试数据库连接
echo "🔍 测试数据库连接..."
$PYTHON_CMD test_mysql_connection.py

# 创建启动脚本
echo "📝 创建启动脚本..."
cat > start_server.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🚀 启动 Work Manager Backend..."
echo "时间: $(date)"
echo "目录: $(pwd)"
echo "端口: ${PORT:-8000}"
echo "================================="

# 设置环境变量
export HOST=0.0.0.0
export PORT=${PORT:-8000}

# 启动服务
python3 main.py
EOF

chmod +x start_server.sh

# 创建后台启动脚本
echo "📝 创建后台启动脚本..."
cat > start_background.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

# 检查是否已经在运行
if [ -f "app.pid" ]; then
    PID=$(cat app.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  服务已在运行 (PID: $PID)"
        echo "如需重启，请先运行: ./stop_server.sh"
        exit 1
    else
        rm -f app.pid
    fi
fi

echo "🚀 后台启动 Work Manager Backend..."
nohup python3 main.py > app.log 2>&1 &
echo $! > app.pid
echo "✅ 服务已启动 (PID: $(cat app.pid))"
echo "📊 查看日志: tail -f app.log"
echo "🛑 停止服务: ./stop_server.sh"
EOF

chmod +x start_background.sh

# 创建停止脚本
echo "📝 创建停止脚本..."
cat > stop_server.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

if [ -f "app.pid" ]; then
    PID=$(cat app.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "🛑 停止服务 (PID: $PID)..."
        kill $PID
        sleep 2
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
    echo "⚠️  未找到 PID 文件，服务可能未运行"
fi
EOF

chmod +x stop_server.sh

# 创建状态检查脚本
echo "📝 创建状态检查脚本..."
cat > check_status.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

echo "📊 Work Manager Backend 状态检查"
echo "================================="

# 检查进程
if [ -f "app.pid" ]; then
    PID=$(cat app.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ 服务运行中 (PID: $PID)"
        
        # 检查端口
        PORT=${PORT:-8000}
        if netstat -tuln 2>/dev/null | grep ":$PORT " > /dev/null; then
            echo "✅ 端口 $PORT 正在监听"
        else
            echo "⚠️  端口 $PORT 未监听"
        fi
        
        # 检查健康状态
        if command -v curl &> /dev/null; then
            echo "🔍 检查健康状态..."
            if curl -s http://localhost:$PORT/health > /dev/null; then
                echo "✅ 健康检查通过"
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
echo "   停止服务: ./stop_server.sh"
echo "   查看日志: tail -f app.log"
echo "   前台运行: ./start_server.sh"
EOF

chmod +x check_status.sh

echo ""
echo "🎉 快速部署完成！"
echo ""
echo "📁 部署目录: $APP_DIR"
echo ""
echo "🚀 启动服务："
echo "   前台运行: ./start_server.sh"
echo "   后台运行: ./start_background.sh"
echo ""
echo "📊 管理命令："
echo "   检查状态: ./check_status.sh"
echo "   停止服务: ./stop_server.sh"
echo "   查看日志: tail -f app.log"
echo ""
echo "🔗 访问地址："
echo "   API 服务: http://your-server-ip:$PORT"
echo "   API 文档: http://your-server-ip:$PORT/docs"
echo "   健康检查: http://your-server-ip:$PORT/health"
echo ""
echo "💡 提示："
echo "   1. 请确保服务器防火墙开放端口 $PORT"
echo "   2. 如需修改配置，请编辑 .env 文件"
echo "   3. 建议使用 screen 或 tmux 保持会话"
echo ""

# 询问是否立即启动
read -p "是否现在启动服务？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 启动服务..."
    ./start_background.sh
    sleep 3
    ./check_status.sh
fi
