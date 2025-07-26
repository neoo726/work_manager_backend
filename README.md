# Work Manager Backend

一个基于 FastAPI 的工作事项管理后端服务，为 Dify AI 助手提供工作事项的记录、查询和更新功能。

## 功能特性

- 智能记录工作事项（任务、会议、问题、想法、笔记等）
- 多条件查询工作事项
- 更新工作事项状态和属性
- 支持时间范围查询
- 项目分类管理
- 优先级和标签系统

## 技术栈

- **FastAPI**: 现代、快速的 Web 框架
- **PostgreSQL**: 关系型数据库
- **Pydantic**: 数据验证和序列化
- **Uvicorn**: ASGI 服务器

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/neoo726/work_manager_backend.git
cd work_manager_backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，配置数据库连接信息
```

### 3. 初始化数据库

```bash
# 运行数据库初始化脚本
python init_db.py
```

### 4. 启动服务

```bash
# 开发模式启动
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式启动
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. 访问 API 文档

启动服务后，访问以下地址查看自动生成的 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 接口

### 记录工作事项
`POST /smart_record_work_item`

智能记录新的工作事项。

### 查询工作事项
`POST /query_work_items`

根据条件查询工作事项。

### 更新工作事项
`POST /update_work_item`

更新现有工作事项的属性。

### 健康检查
`GET /health`

检查服务和数据库连接状态。

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t work-manager-backend .

# 运行容器
docker run -d -p 8000:8000 --env-file .env work-manager-backend
```

### 云服务部署

支持部署到各种云平台：
- Vercel
- Railway
- Render
- 阿里云
- 腾讯云

## 与 Dify 集成

1. 在 Dify 中创建 HTTP 请求工具
2. 导入 `openapi.yaml` 配置文件
3. 配置服务地址
4. 在 Agent 中启用工具

详细配置请参考 `docs/dify-integration.md`

## 许可证

MIT License
