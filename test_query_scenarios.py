#!/usr/bin/env python3
"""
测试不同查询场景
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"
HEADERS = {"Content-Type": "application/json"}

def test_query_scenario(description, query_data):
    """测试查询场景"""
    print(f"\n🔍 {description}")
    print(f"查询参数: {json.dumps(query_data, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/query_work_items",
            headers=HEADERS,
            json=query_data
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"消息: {result.get('message', '')}")
            data = result.get('data', [])
            print(f"找到 {len(data)} 个事项")
            
            if data:
                for item in data:
                    print(f"  - ID {item['id']}: {item['summary']} (截止: {item['due_date']})")
            else:
                print("  没有找到任何事项")
        else:
            print(f"错误: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    print("-" * 50)

def main():
    """主函数"""
    print("🧪 测试不同查询场景")
    print("=" * 60)
    
    # 测试场景
    scenarios = [
        ("查询所有事项", {}),
        ("查询最近的事项 (recent)", {"time_range": "recent"}),
        ("查询过去一周的事项 (past_week)", {"time_range": "past_week"}),
        ("查询今天的事项", {"time_range": "today"}),
        ("查询明天的事项", {"time_range": "tomorrow"}),
        ("查询本周的事项", {"time_range": "this_week"}),
        ("查询任务类型", {"item_type": "task"}),
        ("查询会议类型", {"item_type": "meeting"}),
        ("关键词搜索：任务", {"keyword": "任务"}),
        ("关键词搜索：会议", {"keyword": "会议"}),
        ("查询进行中状态", {"status": "in_progress"}),
        ("查询已完成状态", {"status": "completed"}),
    ]
    
    for description, query_data in scenarios:
        test_query_scenario(description, query_data)

if __name__ == "__main__":
    main()
