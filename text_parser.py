"""
智能文本解析模块 - 识别模糊的时间和查询意图
"""
import re
from datetime import date, timedelta
from typing import Optional, Dict, Any
from models import TimeRange, ItemType, ItemStatus

class QueryParser:
    """查询解析器"""
    
    def __init__(self):
        # 时间相关的关键词映射
        self.time_patterns = {
            # 最近相关
            'recent': [
                r'最近', r'近期', r'这段时间', r'这些天', r'这阵子',
                r'最近的', r'近期的', r'这段时间的'
            ],
            # 今天
            'today': [
                r'今天', r'今日', r'当天', r'本日'
            ],
            # 明天
            'tomorrow': [
                r'明天', r'明日', r'次日'
            ],
            # 本周
            'this_week': [
                r'本周', r'这周', r'这个星期', r'这个礼拜', r'本星期', r'本礼拜'
            ],
            # 下周
            'next_week': [
                r'下周', r'下个星期', r'下个礼拜', r'下星期', r'下礼拜'
            ],
            # 本月
            'this_month': [
                r'本月', r'这个月', r'当月'
            ],
            # 过去一周
            'past_week': [
                r'上周', r'上个星期', r'上个礼拜', r'上星期', r'上礼拜',
                r'过去一周', r'过去的一周', r'前一周'
            ],
            # 过去一个月
            'past_month': [
                r'上个月', r'上月', r'过去一个月', r'过去的一个月', r'前一个月'
            ]
        }
        
        # 事项类型关键词
        self.type_patterns = {
            'task': [
                r'任务', r'工作', r'事项', r'待办', r'要做', r'需要做'
            ],
            'meeting': [
                r'会议', r'开会', r'会面', r'讨论', r'沟通'
            ],
            'issue': [
                r'问题', r'bug', r'故障', r'错误', r'异常'
            ],
            'idea': [
                r'想法', r'点子', r'创意', r'建议', r'方案'
            ],
            'note': [
                r'笔记', r'记录', r'备忘', r'提醒'
            ]
        }
        
        # 状态关键词
        self.status_patterns = {
            'todo': [
                r'待办', r'未开始', r'计划', r'准备'
            ],
            'in_progress': [
                r'进行中', r'正在做', r'在做', r'处理中', r'开发中'
            ],
            'completed': [
                r'完成', r'已完成', r'做完', r'结束', r'已结束'
            ],
            'cancelled': [
                r'取消', r'已取消', r'废弃', r'不做'
            ]
        }
        
        # 查询意图关键词
        self.query_intent_patterns = [
            r'有什么', r'有哪些', r'什么', r'哪些',
            r'查看', r'看看', r'显示', r'列出',
            r'告诉我', r'给我', r'帮我找'
        ]
    
    def parse_query(self, user_input: str) -> Dict[str, Any]:
        """
        解析用户输入，提取查询参数
        
        Args:
            user_input: 用户输入的自然语言
            
        Returns:
            解析后的查询参数字典
        """
        user_input = user_input.lower().strip()
        
        result = {
            'time_range': None,
            'item_type': None,
            'status': None,
            'keyword': None,
            'is_query': False
        }
        
        # 检查是否是查询意图
        for pattern in self.query_intent_patterns:
            if re.search(pattern, user_input):
                result['is_query'] = True
                break
        
        # 解析时间范围
        result['time_range'] = self._parse_time_range(user_input)
        
        # 解析事项类型
        result['item_type'] = self._parse_item_type(user_input)
        
        # 解析状态
        result['status'] = self._parse_status(user_input)
        
        # 提取关键词（移除时间、类型、状态相关词汇后的剩余内容）
        result['keyword'] = self._extract_keyword(user_input)
        
        return result
    
    def _parse_time_range(self, text: str) -> Optional[str]:
        """解析时间范围"""
        for time_range, patterns in self.time_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return time_range
        return None
    
    def _parse_item_type(self, text: str) -> Optional[str]:
        """解析事项类型"""
        for item_type, patterns in self.type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return item_type
        return None
    
    def _parse_status(self, text: str) -> Optional[str]:
        """解析状态"""
        for status, patterns in self.status_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return status
        return None
    
    def _extract_keyword(self, text: str) -> Optional[str]:
        """提取关键词"""
        # 移除常见的查询词汇
        cleaned_text = text
        
        # 移除查询意图词
        for pattern in self.query_intent_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text)
        
        # 移除时间词汇
        for patterns in self.time_patterns.values():
            for pattern in patterns:
                cleaned_text = re.sub(pattern, '', cleaned_text)
        
        # 移除类型词汇
        for patterns in self.type_patterns.values():
            for pattern in patterns:
                cleaned_text = re.sub(pattern, '', cleaned_text)
        
        # 移除状态词汇
        for patterns in self.status_patterns.values():
            for pattern in patterns:
                cleaned_text = re.sub(pattern, '', cleaned_text)
        
        # 清理空格和标点
        cleaned_text = re.sub(r'[，。！？、\s]+', ' ', cleaned_text).strip()
        
        return cleaned_text if cleaned_text and len(cleaned_text) > 1 else None

# 全局解析器实例
query_parser = QueryParser()

def parse_user_query(user_input: str) -> Dict[str, Any]:
    """
    解析用户查询的便捷函数
    
    Args:
        user_input: 用户输入
        
    Returns:
        解析结果
    """
    return query_parser.parse_query(user_input)
