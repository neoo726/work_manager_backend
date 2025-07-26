"""
数据模型定义
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from enum import Enum


class ItemType(str, Enum):
    """工作事项类型枚举"""
    TASK = "task"
    MEETING = "meeting"
    ISSUE = "issue"
    IDEA = "idea"
    NOTE = "note"
    OTHER = "other"


class ItemStatus(str, Enum):
    """工作事项状态枚举"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class TimeRange(str, Enum):
    """时间范围枚举"""
    TODAY = "today"
    TOMORROW = "tomorrow"
    THIS_WEEK = "this_week"
    NEXT_WEEK = "next_week"
    THIS_MONTH = "this_month"
    RECENT = "recent"
    PAST_WEEK = "past_week"
    PAST_MONTH = "past_month"
    ALL = "all"


class SmartRecordWorkItemRequest(BaseModel):
    """智能记录工作事项请求模型"""
    user_input: str = Field(..., description="用户输入的原始文本信息")
    item_type: ItemType = Field(..., description="工作事项的类型")
    summary: str = Field(..., description="工作事项的简要摘要或标题")
    project_name: Optional[str] = Field(None, description="所属项目名称")
    due_date: Optional[date] = Field(None, description="截止日期")
    start_date: Optional[date] = Field(None, description="开始日期")
    status: Optional[ItemStatus] = Field(None, description="当前状态")
    priority: Optional[int] = Field(None, ge=1, le=5, description="优先级，1为最高，5为最低")
    tags: Optional[List[str]] = Field(None, description="相关标签列表")


class QueryWorkItemsRequest(BaseModel):
    """查询工作事项请求模型"""
    time_range: Optional[TimeRange] = Field(None, description="查询的时间范围")
    project_name: Optional[str] = Field(None, description="项目名称")
    item_type: Optional[ItemType] = Field(None, description="工作事项类型")
    status: Optional[ItemStatus] = Field(None, description="工作事项状态")
    keyword: Optional[str] = Field(None, description="关键词搜索")
    item_id: Optional[str] = Field(None, description="特定事项ID")


class UpdateWorkItemRequest(BaseModel):
    """更新工作事项请求模型"""
    user_input: str = Field(..., description="用户原始指令")
    item_id: Optional[str] = Field(None, description="要更新的工作事项ID")
    keyword: Optional[str] = Field(None, description="用于模糊匹配的关键词")
    time_context: Optional[str] = Field(None, description="时间上下文")
    new_status: Optional[ItemStatus] = Field(None, description="新状态")
    new_due_date: Optional[date] = Field(None, description="新截止日期")
    new_priority: Optional[int] = Field(None, ge=1, le=5, description="新优先级")
    new_summary: Optional[str] = Field(None, description="新摘要")
    new_content: Optional[str] = Field(None, description="新详细内容")


class WorkItemResponse(BaseModel):
    """工作事项响应模型"""
    id: str
    type: str
    summary: str
    project_name: Optional[str]
    due_date: Optional[str]
    status: Optional[str]
    priority: Optional[int]
    created_at: Optional[str]
    updated_at: Optional[str]


class ApiResponse(BaseModel):
    """API响应基础模型"""
    message: str
    error: bool = False
    data: Optional[List[WorkItemResponse]] = None


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    message: str
    timestamp: datetime
