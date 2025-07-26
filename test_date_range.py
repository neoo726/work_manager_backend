#!/usr/bin/env python3
"""
测试日期范围计算
"""
from datetime import date, timedelta
from utils import get_date_range
from models import TimeRange

def test_date_ranges():
    """测试不同时间范围的计算"""
    print("📅 测试日期范围计算")
    print("=" * 50)
    
    today = date.today()
    print(f"今天: {today}")
    print()
    
    ranges_to_test = [
        TimeRange.TODAY,
        TimeRange.TOMORROW,
        TimeRange.THIS_WEEK,
        TimeRange.RECENT,
        TimeRange.PAST_WEEK,
        TimeRange.PAST_MONTH,
        TimeRange.ALL
    ]
    
    for time_range in ranges_to_test:
        start_date, end_date = get_date_range(time_range.value)
        print(f"{time_range.value}:")
        print(f"  开始日期: {start_date}")
        print(f"  结束日期: {end_date}")
        
        if start_date and end_date:
            days_diff = (end_date - start_date).days
            print(f"  天数差: {days_diff + 1} 天")
        print()

def check_database_dates():
    """检查数据库中的日期"""
    import pymysql
    from config import settings
    
    print("🗄️ 检查数据库中的日期")
    print("=" * 50)
    
    try:
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
        
        cursor.execute("""
            SELECT id, summary, 
                   DATE(created_at) as created_date,
                   due_date,
                   start_date
            FROM work_items 
            WHERE user_id = 'dify_http_user'
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        
        today = date.today()
        recent_start = today - timedelta(days=7)
        
        print(f"今天: {today}")
        print(f"最近7天范围: {recent_start} 到 {today}")
        print()
        
        for row in rows:
            print(f"ID {row['id']}: {row['summary']}")
            print(f"  创建日期: {row['created_date']}")
            print(f"  截止日期: {row['due_date']}")
            print(f"  开始日期: {row['start_date']}")
            
            # 检查是否在最近7天内
            if row['created_date'] >= recent_start and row['created_date'] <= today:
                print(f"  ✅ 在最近7天内")
            else:
                print(f"  ❌ 不在最近7天内")
            print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    test_date_ranges()
    print()
    check_database_dates()
