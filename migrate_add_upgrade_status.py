import sqlite3
import os

def migrate_add_upgrade_status():
    """添加用户升级审核状态字段"""
    db_path = 'games.sqlite'
    
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'upgrade_status' not in columns:
            # 添加升级审核状态字段
            cursor.execute("ALTER TABLE users ADD COLUMN upgrade_status TEXT DEFAULT 'none'")
            print("已添加 upgrade_status 字段")
        else:
            print("upgrade_status 字段已存在")
            
        if 'upgrade_request_time' not in columns:
            # 添加升级申请时间字段
            cursor.execute("ALTER TABLE users ADD COLUMN upgrade_request_time TEXT")
            print("已添加 upgrade_request_time 字段")
        else:
            print("upgrade_request_time 字段已存在")
            
        conn.commit()
        print("数据库迁移完成")
        
    except Exception as e:
        print(f"迁移失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_add_upgrade_status()