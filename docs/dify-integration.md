# Dify 集成指南

本文档详细说明如何将 Work Manager Backend 与 Dify AI 助手集成。

## 概述

Work Manager Backend 通过 HTTP API 的方式与 Dify 集成，Dify 使用其内置的 "HTTP 请求" 工具来调用我们的后端服务。

## 集成步骤

### 1. 部署后端服务

首先确保 Work Manager Backend 服务已经部署并可以从公网访问。

#### 本地开发测试
```bash
# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000

# 使用 ngrok 暴露到公网（用于测试）
ngrok http 8000
```

#### 生产环境部署
- 云服务器（阿里云、腾讯云、AWS 等）
- Serverless 平台（Vercel、Railway、Render 等）
- Docker 容器部署

### 2. 在 Dify 中配置 HTTP 请求工具

#### 步骤 1：进入工具管理
1. 登录 Dify 控制台
2. 在左侧导航栏找到 **"工具 (Tools)"**
3. 点击 **"创建新工具 (Create New Tool)"**

#### 步骤 2：选择工具类型
选择 **"HTTP 请求 (HTTP Request)"** 工具类型

#### 步骤 3：配置 OpenAPI 规范
选择 **"手动输入 (Manually enter)"** 或 **"导入 JSON/YAML"**，然后导入项目根目录下的 `openapi.yaml` 文件内容。

**重要：** 修改 `openapi.yaml` 中的服务器地址：
```yaml
servers:
  - url: https://your-actual-domain.com  # 替换为你的实际服务地址
    description: 生产环境
```

#### 步骤 4：保存并启用工具
Dify 会验证 OpenAPI 规范，验证通过后保存工具。

### 3. 在 Dify 应用中使用工具

#### 步骤 1：编辑应用
进入你的 Dify 应用（Chatflow 或 Agent）的编排页面。

#### 步骤 2：配置 LLM 节点
1. 点击 LLM 节点（通常是 `Chat` 或 `Agent` 节点）
2. 在配置侧边栏中找到 **"工具 (Tools)"** 部分
3. 启用工具功能
4. 从列表中选择 **"Work Manager API"** 工具

#### 步骤 3：配置系统提示词
为了让 AI 更好地理解何时使用工作事项管理功能，建议在系统提示词中添加：

```
你是一个智能工作助手，可以帮助用户管理工作事项。你有以下能力：

1. 记录工作事项：当用户提到要记录、添加、创建任务、会议、想法等时，使用 smart_record_work_item 工具
2. 查询工作事项：当用户询问今天的任务、本周的会议、某个项目的进度等时，使用 query_work_items 工具
3. 更新工作事项：当用户要求修改、完成、取消某个事项时，使用 update_work_item 工具

请根据用户的自然语言输入，智能判断需要执行的操作，并调用相应的工具。
```

### 4. 测试集成

#### 测试记录功能
用户输入：
```
帮我记录一个任务，明天下午要完成项目报告，优先级设为高
```

AI 应该调用 `smart_record_work_item` 工具，参数类似：
```json
{
  "user_input": "帮我记录一个任务，明天下午要完成项目报告，优先级设为高",
  "item_type": "task",
  "summary": "完成项目报告",
  "due_date": "2024-01-16",
  "priority": 1
}
```

#### 测试查询功能
用户输入：
```
今天有什么任务需要完成？
```

AI 应该调用 `query_work_items` 工具：
```json
{
  "time_range": "today",
  "item_type": "task",
  "status": "todo"
}
```

#### 测试更新功能
用户输入：
```
把项目报告的任务标记为已完成
```

AI 应该调用 `update_work_item` 工具：
```json
{
  "user_input": "把项目报告的任务标记为已完成",
  "keyword": "项目报告",
  "new_status": "completed"
}
```

## 高级配置

### 用户身份识别

默认情况下，所有请求使用 `dify_http_user` 作为用户ID。如果需要支持多用户，可以：

1. 在 Dify 中配置自定义请求头
2. 修改后端代码中的 `get_user_id_from_request` 函数
3. 使用 Dify 的用户上下文变量

### 错误处理

后端服务会返回详细的错误信息，Dify 会将这些信息传递给用户。常见错误：

- `400`: 请求参数错误
- `404`: 找不到指定的工作事项
- `500`: 服务器内部错误

### 性能优化

1. **数据库索引**：已为常用查询字段创建索引
2. **查询限制**：默认限制返回20条记录
3. **连接池**：使用数据库连接池提高性能

## 故障排除

### 常见问题

1. **工具调用失败**
   - 检查服务地址是否正确
   - 确认服务是否正常运行
   - 查看 Dify 的错误日志

2. **数据库连接错误**
   - 检查数据库配置
   - 确认数据库服务是否运行
   - 验证网络连接

3. **权限问题**
   - 检查 CORS 配置
   - 确认防火墙设置
   - 验证 SSL 证书（如果使用 HTTPS）

### 调试技巧

1. **查看 API 文档**：访问 `http://your-domain/docs`
2. **使用测试脚本**：运行 `python test_api.py`
3. **检查日志**：查看应用和数据库日志
4. **健康检查**：访问 `/health` 端点

## 扩展功能

### 添加新的工作事项类型
1. 修改 `models.py` 中的 `ItemType` 枚举
2. 更新 `openapi.yaml` 中的相应定义
3. 在 Dify 中重新导入 OpenAPI 规范

### 自定义字段
1. 修改数据库表结构
2. 更新 Pydantic 模型
3. 修改 API 接口逻辑
4. 更新 OpenAPI 规范

### 集成其他服务
可以扩展后端服务，集成：
- 邮件通知
- 日历同步
- 第三方项目管理工具
- 消息推送服务
