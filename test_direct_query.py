#!/usr/bin/env python3
"""
直接测试智能查询
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"
HEADERS = {"Content-Type": "application/json; charset=utf-8"}

def test_direct_smart_query():
    """直接测试智能查询"""
    print("🧪 直接测试智能查询")
    print("=" * 50)
    
    test_cases = [
        "最近有什么任务",
        "今天有什么会议", 
        "进行中的任务",
        "批量操作",
        "UMS"
    ]
    
    for query in test_cases:
        print(f"\n🔍 查询: '{query}'")
        
        try:
            # 确保使用UTF-8编码
            data = {"user_input": query}
            json_data = json.dumps(data, ensure_ascii=False)
            
            response = requests.post(
                f"{BASE_URL}/smart_query_work_items",
                headers=HEADERS,
                data=json_data.encode('utf-8')
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"消息: {result.get('message', '')}")
                data = result.get('data', [])
                print(f"找到 {len(data)} 个事项")
                
                if data:
                    for item in data[:3]:
                        print(f"  - {item['summary']} ({item['type']})")
            else:
                print(f"错误: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_direct_smart_query()
