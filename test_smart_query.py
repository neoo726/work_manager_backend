#!/usr/bin/env python3
"""
测试智能查询功能
"""
import requests
import json
from text_parser import parse_user_query

BASE_URL = "http://127.0.0.1:8000"
HEADERS = {"Content-Type": "application/json"}

def test_text_parser():
    """测试文本解析器"""
    print("🧠 测试智能文本解析")
    print("=" * 60)
    
    test_inputs = [
        "最近有什么任务",
        "今天有什么会议",
        "明天的工作安排",
        "本周的待办事项",
        "查看进行中的任务",
        "有哪些已完成的工作",
        "UMS相关的任务",
        "最近的会议记录",
        "这个月的项目进展",
        "告诉我所有的问题",
        "看看批量操作的想法"
    ]
    
    for user_input in test_inputs:
        print(f"\n输入: '{user_input}'")
        result = parse_user_query(user_input)
        print(f"解析结果:")
        for key, value in result.items():
            if value is not None:
                print(f"  {key}: {value}")
        print("-" * 40)

def test_smart_query_api():
    """测试智能查询API"""
    print("\n🚀 测试智能查询API")
    print("=" * 60)
    
    test_queries = [
        "最近有什么任务",
        "今天有什么安排",
        "明天的工作",
        "本周的会议",
        "进行中的任务",
        "已完成的工作",
        "UMS相关的内容",
        "批量操作",
        "所有任务"
    ]
    
    for query in test_queries:
        print(f"\n🔍 查询: '{query}'")
        try:
            response = requests.post(
                f"{BASE_URL}/smart_query_work_items",
                headers=HEADERS,
                json={"user_input": query}
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"消息: {result.get('message', '')}")
                data = result.get('data', [])
                print(f"找到 {len(data)} 个事项")
                
                if data:
                    for item in data[:3]:  # 只显示前3个
                        print(f"  - {item['summary']} ({item['type']}) - {item['status']}")
                else:
                    print("  没有找到任何事项")
            else:
                print(f"错误: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
        
        print("-" * 50)

def test_time_range_expansion():
    """测试扩展的时间范围"""
    print("\n📅 测试扩展的时间范围")
    print("=" * 60)
    
    # 测试新的"最近"范围
    try:
        response = requests.post(
            f"{BASE_URL}/query_work_items",
            headers=HEADERS,
            json={"time_range": "recent"}
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"消息: {result.get('message', '')}")
            data = result.get('data', [])
            print(f"'最近'查询找到 {len(data)} 个事项")
            
            if data:
                for item in data:
                    print(f"  - {item['summary']} (截止: {item['due_date']})")
        else:
            print(f"错误: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    # 测试文本解析器
    test_text_parser()
    
    # 测试智能查询API
    test_smart_query_api()
    
    # 测试时间范围扩展
    test_time_range_expansion()
