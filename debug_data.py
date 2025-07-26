#!/usr/bin/env python3
"""
调试数据库中的数据
"""
import pymysql
from config import settings

def debug_database():
    """调试数据库中的数据"""
    try:
        # 连接数据库
        connection_params = {
            'host': settings.db_host,
            'database': settings.db_name,
            'user': settings.db_user,
            'password': settings.db_password,
            'port': settings.db_port,
            'charset': 'utf8mb4'
        }
        
        conn = pymysql.connect(**connection_params)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        print("🔍 查看数据库中的所有工作事项:")
        print("=" * 80)
        
        # 查询所有记录
        cursor.execute("""
            SELECT id, user_id, type, summary, project_name, due_date, start_date, 
                   status, priority, created_at, updated_at
            FROM work_items 
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("❌ 数据库中没有任何记录")
            return
            
        print(f"📊 找到 {len(rows)} 条记录:")
        print()
        
        for i, row in enumerate(rows, 1):
            print(f"记录 {i}:")
            print(f"  ID: {row['id']}")
            print(f"  用户ID: '{row['user_id']}'")
            print(f"  类型: {row['type']}")
            print(f"  摘要: {row['summary']}")
            print(f"  项目: {row['project_name']}")
            print(f"  截止日期: {row['due_date']}")
            print(f"  开始日期: {row['start_date']}")
            print(f"  状态: {row['status']}")
            print(f"  优先级: {row['priority']}")
            print(f"  创建时间: {row['created_at']}")
            print(f"  更新时间: {row['updated_at']}")
            print("-" * 40)
        
        # 统计不同用户ID的记录数
        cursor.execute("""
            SELECT user_id, COUNT(*) as count 
            FROM work_items 
            GROUP BY user_id
        """)
        
        user_stats = cursor.fetchall()
        print("\n📈 用户ID统计:")
        for stat in user_stats:
            print(f"  用户ID '{stat['user_id']}': {stat['count']} 条记录")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    debug_database()
