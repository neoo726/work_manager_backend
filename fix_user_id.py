#!/usr/bin/env python3
"""
修复用户ID问题 - 将所有记录的用户ID统一为 'dify_http_user'
"""
import pymysql
from config import settings

def fix_user_ids():
    """将所有记录的用户ID统一为 'dify_http_user'"""
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
        
        print("🔧 修复用户ID问题...")
        print("=" * 50)
        
        # 查看当前状态
        cursor.execute("SELECT user_id, COUNT(*) as count FROM work_items GROUP BY user_id")
        before_stats = cursor.fetchall()
        
        print("修复前的用户ID统计:")
        for stat in before_stats:
            print(f"  用户ID '{stat['user_id']}': {stat['count']} 条记录")
        
        # 将所有记录的用户ID更新为 'dify_http_user'
        cursor.execute("""
            UPDATE work_items 
            SET user_id = 'dify_http_user' 
            WHERE user_id != 'dify_http_user'
        """)
        
        affected_rows = cursor.rowcount
        conn.commit()
        
        print(f"\n✅ 已更新 {affected_rows} 条记录的用户ID")
        
        # 查看修复后状态
        cursor.execute("SELECT user_id, COUNT(*) as count FROM work_items GROUP BY user_id")
        after_stats = cursor.fetchall()
        
        print("\n修复后的用户ID统计:")
        for stat in after_stats:
            print(f"  用户ID '{stat['user_id']}': {stat['count']} 条记录")
        
        # 显示所有记录
        cursor.execute("""
            SELECT id, user_id, type, summary, due_date, created_at
            FROM work_items 
            ORDER BY created_at DESC
        """)
        
        all_records = cursor.fetchall()
        print(f"\n📋 所有记录 (共 {len(all_records)} 条):")
        for record in all_records:
            print(f"  ID {record['id']}: {record['summary']} (用户: {record['user_id']})")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 用户ID修复完成！现在Dify应该能查询到所有工作事项了。")
        
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    fix_user_ids()
