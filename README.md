# Work Manager Backend

一个基于 FastAPI 的智能工作事项管理后端服务，为 Dify AI 助手提供工作事项的记录、查询和更新功能。支持自然语言输入和智能解析。

## 🚀 功能特性

### 核心功能
- **智能记录**：支持自然语言输入，自动解析工作事项信息
- **智能查询**：支持模糊查询和自然语言查询，如"最近有什么任务"
- **多条件查询**：按时间、类型、状态、项目、关键词等条件查询
- **状态管理**：更新工作事项状态和属性
- **时间智能**：支持灵活的时间范围表达和查询

### 增强特性
- **扩展时间范围**："最近"查询覆盖过去2周到未来2周
- **自然语言解析**：理解各种时间表达方式和查询意图
- **混合查询逻辑**：结合创建时间、截止日期和开始日期的智能查询
- **用户隔离**：支持多用户数据隔离
- **详细日志**：完整的调试和监控日志

## 🛠 技术栈

- **FastAPI**: 现代、快速的 Web 框架
- **MySQL**: 关系型数据库（支持云数据库）
- **Pydantic**: 数据验证和序列化
- **Uvicorn**: ASGI 服务器
- **PyMySQL**: MySQL 数据库连接器
- **自然语言处理**: 内置智能文本解析器

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

## 📡 API 接口

### 智能记录工作事项
`POST /smart_record_work_item`

智能记录新的工作事项，支持自然语言输入。

**示例输入：**
```json
{
  "user_input": "明天下午3点开会讨论项目进展",
  "summary": "项目进展讨论会议",
  "item_type": "meeting",
  "due_date": "2025-07-27",
  "priority": 2
}
```

### 标准查询工作事项
`POST /query_work_items`

根据结构化条件查询工作事项。

**示例输入：**
```json
{
  "time_range": "recent",
  "item_type": "task",
  "status": "in_progress",
  "keyword": "项目"
}
```

### 🧠 智能查询工作事项（新增）
`POST /smart_query_work_items`

支持自然语言查询，自动解析查询意图。

**示例输入：**
```json
{
  "user_input": "最近有什么任务"
}
```

**支持的自然语言查询：**
- "最近有什么任务"
- "今天有什么会议"
- "进行中的工作"
- "明天的安排"
- "本周的待办事项"
- "UMS相关的任务"

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

## 🤖 与 Dify 集成

### 基本集成
1. 在 Dify 中创建 HTTP 请求工具
2. 导入 `openapi.yaml` 配置文件
3. 配置服务地址
4. 在 Agent 中启用工具

### 推荐工作流配置
```
开始 → 知识库检索 → 代码执行 → HTTP请求 → 结束
```

**建议使用智能查询端点：**
- 对于自然语言查询：使用 `/smart_query_work_items`
- 对于结构化查询：使用 `/query_work_items`

### 知识库内容建议
- 使用指南和示例
- 时间表达方式说明
- 任务类型和状态说明
- 常见问题解答

详细配置请参考 `docs/dify-integration.md`

## 🔧 开发和测试

### 运行测试
```bash
# 测试数据库连接
python test_mysql_connection.py

# 测试API接口
python test_api.py

# 测试智能查询
python test_smart_query.py

# 测试时间范围
python test_date_range.py
```

### 调试工具
```bash
# 查看数据库数据
python debug_data.py

# 修复用户ID问题
python fix_user_id.py
```

## 许可证

MIT License
