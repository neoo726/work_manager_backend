-- Work Manager 数据库初始化脚本 (MySQL版本)
-- 创建工作事项管理所需的数据库表结构

-- 删除已存在的表（如果存在）
DROP TABLE IF EXISTS work_items;

-- 创建工作事项表
CREATE TABLE work_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    type ENUM('task', 'meeting', 'issue', 'idea', 'note', 'other') NOT NULL,
    content TEXT NOT NULL,
    summary VARCHAR(500) NOT NULL,
    project_name VARCHAR(255),
    due_date DATE,
    start_date DATE,
    status ENUM('todo', 'in_progress', 'completed', 'resolved', 'cancelled'),
    priority INT CHECK (priority >= 1 AND priority <= 5),
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建索引以提高查询性能
CREATE INDEX idx_work_items_user_id ON work_items(user_id);
CREATE INDEX idx_work_items_type ON work_items(type);
CREATE INDEX idx_work_items_status ON work_items(status);
CREATE INDEX idx_work_items_due_date ON work_items(due_date);
CREATE INDEX idx_work_items_start_date ON work_items(start_date);
CREATE INDEX idx_work_items_project_name ON work_items(project_name);
CREATE INDEX idx_work_items_created_at ON work_items(created_at);
CREATE INDEX idx_work_items_updated_at ON work_items(updated_at);

-- 创建全文搜索索引 (MySQL版本)
CREATE FULLTEXT INDEX idx_work_items_summary_fulltext ON work_items(summary);
CREATE FULLTEXT INDEX idx_work_items_content_fulltext ON work_items(content);

-- 创建复合索引
CREATE INDEX idx_work_items_user_status ON work_items(user_id, status);
CREATE INDEX idx_work_items_user_type ON work_items(user_id, type);
CREATE INDEX idx_work_items_user_project ON work_items(user_id, project_name);

-- 插入示例数据（可选）
INSERT INTO work_items (
    user_id, type, content, summary, project_name,
    due_date, start_date, status, priority, tags
) VALUES
(
    'dify_http_user',
    'task',
    '完成 Work Manager 后端服务的开发和测试',
    '开发 Work Manager 后端服务',
    'Work Manager',
    DATE_ADD(CURDATE(), INTERVAL 7 DAY),
    CURDATE(),
    'in_progress',
    2,
    JSON_ARRAY('开发', '后端', 'FastAPI')
),
(
    'dify_http_user',
    'meeting',
    '与团队讨论项目进度和下一步计划',
    '项目进度会议',
    'Work Manager',
    DATE_ADD(CURDATE(), INTERVAL 2 DAY),
    DATE_ADD(CURDATE(), INTERVAL 2 DAY),
    'todo',
    3,
    JSON_ARRAY('会议', '团队', '计划')
),
(
    'dify_http_user',
    'idea',
    '考虑添加工作事项的优先级自动调整功能',
    '优先级自动调整功能',
    'Work Manager',
    NULL,
    NULL,
    'todo',
    4,
    JSON_ARRAY('功能', '优化', '自动化')
);

-- MySQL 中 updated_at 字段已经通过 ON UPDATE CURRENT_TIMESTAMP 自动更新
-- 不需要额外的触发器

-- 显示表结构
DESCRIBE work_items;

-- 显示示例数据
SELECT id, type, summary, project_name, status, priority, created_at
FROM work_items
ORDER BY created_at DESC;
