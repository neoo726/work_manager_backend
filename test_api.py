#!/usr/bin/env python3
"""
Work Manager Backend API 测试脚本
"""
import requests
import json
from datetime import date, timedelta
import time

# 配置
BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json",
    "X-Dify-User-ID": "test_user"
}

def test_health():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_record_work_item():
    """测试记录工作事项接口"""
    print("\n📝 测试记录工作事项接口...")
    
    test_items = [
        {
            "user_input": "明天下午3点有个重要的项目会议，需要准备演示文稿",
            "item_type": "meeting",
            "summary": "项目会议 - 准备演示文稿",
            "project_name": "Work Manager",
            "due_date": str(date.today() + timedelta(days=1)),
            "status": "todo",
            "priority": 2,
            "tags": ["会议", "演示", "项目"]
        },
        {
            "user_input": "完成用户认证模块的开发和测试",
            "item_type": "task",
            "summary": "开发用户认证模块",
            "project_name": "Work Manager",
            "due_date": str(date.today() + timedelta(days=7)),
            "status": "in_progress",
            "priority": 1,
            "tags": ["开发", "认证", "测试"]
        },
        {
            "user_input": "考虑添加工作事项的批量操作功能",
            "item_type": "idea",
            "summary": "批量操作功能",
            "project_name": "Work Manager",
            "priority": 3,
            "tags": ["功能", "批量", "优化"]
        }
    ]
    
    created_items = []
    for item in test_items:
        try:
            response = requests.post(
                f"{BASE_URL}/smart_record_work_item",
                headers=HEADERS,
                json=item
            )
            print(f"状态码: {response.status_code}")
            result = response.json()
            print(f"响应: {result}")
            
            if response.status_code == 200:
                created_items.append(item)
                print(f"✅ 成功记录: {item['summary']}")
            else:
                print(f"❌ 记录失败: {item['summary']}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    return created_items

def test_query_work_items():
    """测试查询工作事项接口"""
    print("\n🔍 测试查询工作事项接口...")
    
    test_queries = [
        {
            "description": "查询所有事项",
            "query": {}
        },
        {
            "description": "查询今天的事项",
            "query": {"time_range": "today"}
        },
        {
            "description": "查询任务类型",
            "query": {"item_type": "task"}
        },
        {
            "description": "查询Work Manager项目",
            "query": {"project_name": "Work Manager"}
        },
        {
            "description": "关键词搜索",
            "query": {"keyword": "会议"}
        }
    ]
    
    for test in test_queries:
        print(f"\n📋 {test['description']}")
        try:
            response = requests.post(
                f"{BASE_URL}/query_work_items",
                headers=HEADERS,
                json=test['query']
            )
            print(f"状态码: {response.status_code}")
            result = response.json()
            print(f"找到 {len(result.get('data', []))} 个事项")
            
            if result.get('data'):
                for item in result['data'][:2]:  # 只显示前2个
                    print(f"  - {item['summary']} ({item['type']}) - {item['status']}")
                    
        except Exception as e:
            print(f"❌ 查询失败: {e}")

def test_update_work_item():
    """测试更新工作事项接口"""
    print("\n✏️ 测试更新工作事项接口...")
    
    # 首先查询一个事项来更新
    try:
        response = requests.post(
            f"{BASE_URL}/query_work_items",
            headers=HEADERS,
            json={"keyword": "会议"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('data'):
                item_id = result['data'][0]['id']
                print(f"找到事项ID: {item_id}")
                
                # 更新状态
                update_data = {
                    "user_input": "将会议状态更新为已完成",
                    "item_id": item_id,
                    "new_status": "completed"
                }
                
                response = requests.post(
                    f"{BASE_URL}/update_work_item",
                    headers=HEADERS,
                    json=update_data
                )
                
                print(f"状态码: {response.status_code}")
                result = response.json()
                print(f"响应: {result}")
                
                if response.status_code == 200:
                    print("✅ 更新成功")
                else:
                    print("❌ 更新失败")
            else:
                print("没有找到可更新的事项")
        else:
            print("查询事项失败")
            
    except Exception as e:
        print(f"❌ 更新失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试 Work Manager Backend API")
    print("=" * 50)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)
    
    # 测试健康检查
    if not test_health():
        print("❌ 服务未正常运行，请检查服务状态")
        return
    
    # 测试记录工作事项
    created_items = test_record_work_item()
    
    # 等待数据写入
    time.sleep(1)
    
    # 测试查询工作事项
    test_query_work_items()
    
    # 测试更新工作事项
    test_update_work_item()
    
    print("\n" + "=" * 50)
    print("🎉 API 测试完成")
    print(f"📊 创建了 {len(created_items)} 个测试事项")
    print("💡 可以访问 http://localhost:8000/docs 查看API文档")

if __name__ == "__main__":
    main()
