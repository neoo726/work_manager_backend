"""
工具函数模块
"""
from datetime import date, timedelta
from typing import Tuple, Optional
from models import TimeRange


def get_date_range(time_range: str) -> Tuple[Optional[date], Optional[date]]:
    """
    根据时间范围字符串计算开始和结束日期
    
    Args:
        time_range: 时间范围字符串
        
    Returns:
        (start_date, end_date) 元组，如果是 'all' 则返回 (None, None)
    """
    today = date.today()
    
    if time_range == TimeRange.TODAY:
        return today, today
    elif time_range == TimeRange.TOMORROW:
        tomorrow = today + timedelta(days=1)
        return tomorrow, tomorrow
    elif time_range == TimeRange.THIS_WEEK:
        # 本周：从周一到周日
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return start_of_week, end_of_week
    elif time_range == TimeRange.NEXT_WEEK:
        # 下周：从下周一到下周日
        start_of_next_week = today + timedelta(days=7 - today.weekday())
        end_of_next_week = start_of_next_week + timedelta(days=6)
        return start_of_next_week, end_of_next_week
    elif time_range == TimeRange.THIS_MONTH:
        # 本月：从月初到月末
        start_of_month = today.replace(day=1)
        # 计算下个月的第一天，然后减去一天得到本月最后一天
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
        end_of_month = next_month - timedelta(days=1)
        return start_of_month, end_of_month
    elif time_range == TimeRange.RECENT or time_range == TimeRange.PAST_WEEK:
        # 最近一周：过去7天到今天
        return today - timedelta(days=7), today
    elif time_range == TimeRange.PAST_MONTH:
        # 过去一个月：过去30天到今天
        return today - timedelta(days=30), today
    elif time_range == TimeRange.ALL:
        # 所有时间
        return None, None
    else:
        # 默认返回所有时间
        return None, None


def format_work_item_for_display(item: dict) -> str:
    """
    格式化工作事项用于显示
    
    Args:
        item: 工作事项字典
        
    Returns:
        格式化后的字符串
    """
    parts = []
    
    # 基本信息
    parts.append(f"ID: {item.get('id', 'N/A')}")
    parts.append(f"类型: {item.get('type', 'N/A')}")
    parts.append(f"摘要: {item.get('summary', 'N/A')}")
    
    # 可选信息
    if item.get('project_name'):
        parts.append(f"项目: {item['project_name']}")
    
    if item.get('status'):
        parts.append(f"状态: {item['status']}")
    
    if item.get('priority'):
        parts.append(f"优先级: {item['priority']}")
    
    if item.get('due_date'):
        parts.append(f"截止日期: {item['due_date']}")
    
    return " | ".join(parts)


def validate_priority(priority: Optional[int]) -> bool:
    """
    验证优先级是否有效
    
    Args:
        priority: 优先级值
        
    Returns:
        是否有效
    """
    if priority is None:
        return True
    return 1 <= priority <= 5


def get_user_id_from_request(headers: dict) -> str:
    """
    从请求头中获取用户ID
    
    Args:
        headers: 请求头字典
        
    Returns:
        用户ID，如果没有则返回默认值
    """
    # 尝试从不同的请求头中获取用户ID
    user_id = (
        headers.get('x-dify-user-id') or
        headers.get('x-user-id') or
        headers.get('user-id') or
        'dify_http_user'  # 默认用户ID
    )
    return user_id
