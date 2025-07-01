#!/usr/bin/env python3
"""
数据库迁移脚本：为游戏表添加is_official字段
"""

import sqlite3
import os

def migrate_database():
    """执行数据库迁移"""
    db_path = 'games.sqlite'
    
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(games)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_official' not in columns:
            print("添加 is_official 字段...")
            cursor.execute("ALTER TABLE games ADD COLUMN is_official INTEGER DEFAULT 0")
            
            # 为现有包含[官方]的游戏设置标识
            cursor.execute("UPDATE games SET is_official = 1 WHERE name LIKE '%[官方]%'")
            
            # 移除游戏名称中的[官方]后缀
            cursor.execute("UPDATE games SET name = REPLACE(name, ' [官方]', '') WHERE name LIKE '% [官方]%'")
            cursor.execute("UPDATE games SET name = REPLACE(name, '[官方]', '') WHERE name LIKE '%[官方]%'")
            
            conn.commit()
            print("迁移完成！")
            
            # 显示更新结果
            cursor.execute("SELECT COUNT(*) FROM games WHERE is_official = 1")
            official_count = cursor.fetchone()[0]
            print(f"标记为官方的游戏数量: {official_count}")
            
        else:
            print("is_official 字段已存在，跳过迁移")
        
        conn.close()
        
    except Exception as e:
        print(f"迁移失败: {e}")
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database() 
 
 
 
 
 
 