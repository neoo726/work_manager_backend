#!/usr/bin/env python3
"""
Work Manager Backend 启动脚本
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """检查依赖是否已安装"""
    try:
        import fastapi
        import uvicorn
        import psycopg2
        import pydantic
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_env_file():
    """检查环境变量文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env 文件不存在")
        print("请复制 .env.example 到 .env 并配置数据库连接信息")
        
        # 自动复制 .env.example
        example_file = Path(".env.example")
        if example_file.exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ 已自动创建 .env 文件，请编辑其中的数据库配置")
        return False
    else:
        print("✅ .env 文件存在")
        return True

def test_database_connection():
    """测试数据库连接"""
    try:
        from database import db_manager
        if db_manager.test_connection():
            print("✅ 数据库连接成功")
            return True
        else:
            print("❌ 数据库连接失败")
            return False
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        print("请检查数据库配置和服务状态")
        return False

def init_database():
    """初始化数据库"""
    print("🔧 初始化数据库...")
    try:
        result = subprocess.run([sys.executable, "init_db.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 数据库初始化成功")
            return True
        else:
            print(f"❌ 数据库初始化失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 数据库初始化异常: {e}")
        return False

def start_server():
    """启动服务器"""
    print("🚀 启动 Work Manager Backend 服务...")
    try:
        # 使用 uvicorn 启动服务
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ]
        
        print("启动命令:", " ".join(cmd))
        print("服务将在 http://localhost:8000 启动")
        print("API 文档: http://localhost:8000/docs")
        print("按 Ctrl+C 停止服务")
        print("-" * 50)
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动服务失败: {e}")

def main():
    """主函数"""
    print("🎯 Work Manager Backend 启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_requirements():
        sys.exit(1)
    
    # 检查环境文件
    env_exists = check_env_file()
    
    # 如果环境文件不存在，给用户时间配置
    if not env_exists:
        print("\n请编辑 .env 文件配置数据库连接信息，然后重新运行此脚本")
        sys.exit(1)
    
    # 测试数据库连接
    if not test_database_connection():
        print("\n数据库连接失败，是否要初始化数据库？(y/n): ", end="")
        choice = input().lower().strip()
        
        if choice == 'y':
            if not init_database():
                print("数据库初始化失败，请检查配置")
                sys.exit(1)
        else:
            print("请确保数据库服务正在运行并且配置正确")
            sys.exit(1)
    
    print("\n✅ 所有检查通过，准备启动服务...")
    time.sleep(1)
    
    # 启动服务
    start_server()

if __name__ == "__main__":
    main()
