import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'mock.db')

def init_db_manual():
    print(f"数据库路径: {DB_PATH}")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 先检查 mock_group 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mock_group'")
    if not cursor.fetchone():
        print("创建 mock_group 表...")
        cursor.execute('''
            CREATE TABLE mock_group (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER DEFAULT 0,
                sort_order INTEGER DEFAULT 0,
                icon TEXT DEFAULT '📁',
                color TEXT DEFAULT '#667eea',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        conn.commit()
        print("✅ mock_group 表创建成功！")
    
    # 2. 检查 mock_config 表是否有 group_id 列
    cursor.execute("PRAGMA table_info(mock_config)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"当前 mock_config 列: {columns}")
    if 'group_id' not in columns:
        print("添加 group_id 列...")
        cursor.execute("ALTER TABLE mock_config ADD COLUMN group_id INTEGER DEFAULT 0")
        conn.commit()
        print("✅ group_id 添加成功！")
    
    # 3. 检查是否有目录数据
    cursor.execute("SELECT COUNT(*) FROM mock_group")
    count = cursor.fetchone()[0]
    if count == 0:
        print("插入默认目录...")
        now = datetime.now().isoformat()
        default_groups = [
            ('用户中心', 0, 1, '👤', '#667eea'),
            ('商品管理', 0, 2, '📦', '#764ba2'),
            ('订单系统', 0, 3, '📋', '#f093fb'),
            ('支付系统', 0, 4, '💰', '#f5576c'),
        ]
        for name, parent_id, sort_order, icon, color in default_groups:
            cursor.execute('''
                INSERT INTO mock_group (name, parent_id, sort_order, icon, color, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, parent_id, sort_order, icon, color, now, now))
        conn.commit()
        print(f"✅ 插入了 {len(default_groups)} 个目录！")
    else:
        print(f"已有 {count} 个目录，无需插入")
    
    # 4. 测试获取
    cursor.execute("SELECT * FROM mock_group")
    groups = cursor.fetchall()
    print(f"\n当前目录: {groups}")
    
    conn.close()
    print("\n✅ 完成！")

if __name__ == "__main__":
    init_db_manual()
