import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'mock.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建mock_group表：存储目录树
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mock_group (
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
    
    # 创建mock_config表：存储Mock配置
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mock_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            group_id INTEGER DEFAULT 0,
            method TEXT NOT NULL,
            url_pattern TEXT NOT NULL,
            url_match_type TEXT NOT NULL DEFAULT 'exact',
            request_headers TEXT,
            request_query TEXT,
            request_body TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # 创建mock_response表：存储多个响应
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mock_response (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            response_status INTEGER NOT NULL DEFAULT 200,
            response_headers TEXT,
            response_body TEXT,
            response_delay INTEGER DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 0,
            sort_order INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (config_id) REFERENCES mock_config(id)
        )
    ''')
    
    # request_log表：存储请求日志
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS request_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_method TEXT NOT NULL,
            request_url TEXT NOT NULL,
            request_headers TEXT,
            request_query TEXT,
            request_body TEXT,
            response_status INTEGER,
            response_headers TEXT,
            response_body TEXT,
            response_delay INTEGER,
            matched_config_id INTEGER,
            matched_response_id INTEGER,
            matched_config_url TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def migrate_old_data():
    """从旧表结构迁移数据到新结构"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 1. 检查并添加 group_id 字段到 mock_config 表
        cursor.execute("PRAGMA table_info(mock_config)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"当前 mock_config 列: {columns}")
        
        if 'group_id' not in columns:
            print("添加 group_id 列...")
            cursor.execute("ALTER TABLE mock_config ADD COLUMN group_id INTEGER DEFAULT 0")
            conn.commit()
            print("✅ 已添加 group_id 字段到 mock_config")
        
        # 2. 检查旧表是否还有response字段
        if 'response_body' in columns:
            # 迁移旧数据
            cursor.execute("SELECT * FROM mock_config WHERE is_active = 1")
            old_configs = cursor.fetchall()
            
            for config in old_configs:
                config_dict = dict(config)
                # 为每个旧配置创建一个响应
                if config_dict.get('response_body'):
                    add_mock_response({
                        'config_id': config_dict['id'],
                        'name': '默认响应',
                        'response_status': config_dict.get('response_status', 200),
                        'response_headers': config_dict.get('response_headers'),
                        'response_body': config_dict.get('response_body'),
                        'response_delay': config_dict.get('response_delay', 0),
                        'is_active': 1
                    })
            
            print(f"迁移了 {len(old_configs)} 条配置")
            
    except Exception as e:
        print(f"迁移出错: {e}")
        import traceback
        traceback.print_exc()
    
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Mock配置CRUD
def add_mock_config(config):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO mock_config 
        (name, group_id, method, url_pattern, url_match_type, request_headers, request_query, request_body, 
         is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        config['name'], config.get('group_id', 0), config['method'], config['url_pattern'], config.get('url_match_type', 'exact'),
        config.get('request_headers'), config.get('request_query'), config.get('request_body'),
        config.get('is_active', 1), now, now
    ))
    conn.commit()
    config_id = cursor.lastrowid
    conn.close()
    return config_id

def get_all_mock_configs():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mock_config WHERE is_active = 1 ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_mock_configs_paginated(page=1, page_size=10, name=None, method=None, url_pattern=None, date_start=None, date_end=None):
    conn = get_db()
    cursor = conn.cursor()
    
    # 构建查询条件
    where_clauses = ['is_active = 1']
    params = []
    
    if name:
        where_clauses.append('name LIKE ?')
        params.append(f'%{name}%')
    if method:
        where_clauses.append('method = ?')
        params.append(method)
    if url_pattern:
        where_clauses.append('url_pattern LIKE ?')
        params.append(f'%{url_pattern}%')
    if date_start:
        where_clauses.append('created_at >= ?')
        params.append(date_start)
    if date_end:
        where_clauses.append('created_at <= ?')
        params.append(f'{date_end}T23:59:59')
    
    where_query = ' AND '.join(where_clauses)
    
    # 获取总数
    cursor.execute(f'SELECT COUNT(*) as total FROM mock_config WHERE {where_query}', params)
    total = cursor.fetchone()['total']
    
    # 获取分页数据
    offset = (page - 1) * page_size
    cursor.execute(
        f'SELECT * FROM mock_config WHERE {where_query} ORDER BY id DESC LIMIT ? OFFSET ?',
        params + [page_size, offset]
    )
    rows = cursor.fetchall()
    configs = [dict(row) for row in rows]
    
    # 获取所有配置的响应数据
    if configs:
        config_ids = [c['id'] for c in configs]
        placeholders = ','.join(['?' for _ in config_ids])
        cursor.execute(f'SELECT * FROM mock_response WHERE config_id IN ({placeholders})', config_ids)
        all_responses = [dict(r) for r in cursor.fetchall()]
        
        # 把响应数据关联到对应的配置
        for config in configs:
            config['responses'] = [r for r in all_responses if r['config_id'] == config['id']]
    
    conn.close()
    
    return {
        'items': configs,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size if total > 0 else 1
    }

def get_mock_config_by_id(config_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mock_config WHERE id = ?', (config_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_mock_config(config_id, config):
    print(f"开始更新配置 {config_id}, data={config}")
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    # 先检查是否存在
    cursor.execute("SELECT * FROM mock_config WHERE id = ?", (config_id,))
    existing = cursor.fetchone()
    if not existing:
        print(f"❌ 配置 {config_id} 不存在！")
        conn.close()
        return
    
    try:
        cursor.execute('''
            UPDATE mock_config SET
            name = ?, group_id = ?, method = ?, url_pattern = ?, url_match_type = ?, request_headers = ?, 
            request_query = ?, request_body = ?, is_active = ?, updated_at = ?
            WHERE id = ?
        ''', (
            config['name'], config.get('group_id', 0), config['method'], config['url_pattern'], config.get('url_match_type', 'exact'),
            config.get('request_headers'), config.get('request_query'), config.get('request_body'),
            config.get('is_active', 1), now, config_id
        ))
        conn.commit()
        print(f"✅ 更新配置 {config_id} 成功！")
    except Exception as e:
        print(f"❌ 更新配置失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def delete_mock_config(config_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE mock_config SET is_active = 0 WHERE id = ?', (config_id,))
    # 同时删除关联的响应
    cursor.execute('DELETE FROM mock_response WHERE config_id = ?', (config_id,))
    conn.commit()
    conn.close()

# Mock响应CRUD
def add_mock_response(response):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    # 获取当前最大排序
    cursor.execute('SELECT MAX(sort_order) as max_sort FROM mock_response WHERE config_id = ?', 
                   (response['config_id'],))
    max_sort = cursor.fetchone()['max_sort'] or 0
    
    cursor.execute('''
        INSERT INTO mock_response 
        (config_id, name, response_status, response_headers, response_body, response_delay, 
         is_active, sort_order, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        response['config_id'], response['name'], response.get('response_status', 200),
        response.get('response_headers'), response.get('response_body'),
        response.get('response_delay', 0), response.get('is_active', 0),
        max_sort + 1, now, now
    ))
    conn.commit()
    response_id = cursor.lastrowid
    conn.close()
    return response_id

def get_responses_by_config_id(config_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM mock_response 
        WHERE config_id = ? 
        ORDER BY sort_order ASC, id DESC
    ''', (config_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_active_response_by_config_id(config_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM mock_response 
        WHERE config_id = ? AND is_active = 1
        ORDER BY sort_order ASC
        LIMIT 1
    ''', (config_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_mock_response(response_id, response):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('''
        UPDATE mock_response SET
        name = ?, response_status = ?, response_headers = ?, response_body = ?, 
        response_delay = ?, is_active = ?, updated_at = ?
        WHERE id = ?
    ''', (
        response['name'], response.get('response_status', 200),
        response.get('response_headers'), response.get('response_body'),
        response.get('response_delay', 0), response.get('is_active', 0), now, response_id
    ))
    conn.commit()
    conn.close()

def delete_mock_response(response_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM mock_response WHERE id = ?', (response_id,))
    conn.commit()
    conn.close()

def set_response_active(response_id, is_active):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    # 先获取该响应的配置ID
    cursor.execute('SELECT config_id FROM mock_response WHERE id = ?', (response_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return
    
    config_id = row['config_id']
    
    if is_active:
        # 如果要激活，先把该配置下的其他响应都设为非激活
        cursor.execute('UPDATE mock_response SET is_active = 0, updated_at = ? WHERE config_id = ?', 
                       (now, config_id))
    
    # 设置当前响应状态
    cursor.execute('UPDATE mock_response SET is_active = ?, updated_at = ? WHERE id = ?', 
                   (1 if is_active else 0, now, response_id))
    conn.commit()
    conn.close()

# 请求日志
def add_request_log(log):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO request_log 
        (request_method, request_url, request_headers, request_query, request_body,
         response_status, response_headers, response_body, response_delay, 
         matched_config_id, matched_response_id, matched_config_url, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        log['request_method'], log['request_url'], log.get('request_headers'), log.get('request_query'),
        log.get('request_body'), log.get('response_status'), log.get('response_headers'),
        log.get('response_body'), log.get('response_delay'), log.get('matched_config_id'),
        log.get('matched_response_id'), log.get('matched_config_url'), now
    ))
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id

def get_recent_logs(limit=50):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM request_log ORDER BY id DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_logs_paginated(page=1, page_size=10, url=None, mock_url=None, date_start=None, date_end=None):
    conn = get_db()
    cursor = conn.cursor()
    
    # 构建查询条件
    where_clauses = []
    params = []
    
    if url:
        where_clauses.append('request_url LIKE ?')
        params.append(f'%{url}%')
    if mock_url:
        where_clauses.append('matched_config_url LIKE ?')
        params.append(f'%{mock_url}%')
    if date_start:
        where_clauses.append('created_at >= ?')
        params.append(date_start)
    if date_end:
        where_clauses.append('created_at <= ?')
        params.append(f'{date_end}T23:59:59')
    
    where_query = ' AND '.join(where_clauses) if where_clauses else '1=1'
    
    # 获取总数
    cursor.execute(f'SELECT COUNT(*) as total FROM request_log WHERE {where_query}', params)
    total = cursor.fetchone()['total']
    
    # 获取分页数据
    offset = (page - 1) * page_size
    cursor.execute(
        f'SELECT * FROM request_log WHERE {where_query} ORDER BY id DESC LIMIT ? OFFSET ?',
        params + [page_size, offset]
    )
    rows = cursor.fetchall()
    conn.close()
    
    return {
        'items': [dict(row) for row in rows],
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size if total > 0 else 1
    }


# ==================== 目录树相关函数 ====================
def add_mock_group(group):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO mock_group 
        (name, parent_id, sort_order, icon, color, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        group.get('name'),
        group.get('parent_id', 0),
        group.get('sort_order', 0),
        group.get('icon', '📁'),
        group.get('color', '#667eea'),
        now, now
    ))
    group_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return group_id


def get_all_groups():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mock_group ORDER BY sort_order ASC, id ASC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def build_group_tree(groups):
    tree = []
    group_dict = {g['id']: {**g, 'children': []} for g in groups}
    
    for group in groups:
        if group['parent_id'] == 0:
            tree.append(group_dict[group['id']])
        else:
            if group['parent_id'] in group_dict:
                group_dict[group['parent_id']]['children'].append(group_dict[group['id']])
    return tree


def get_group_tree():
    groups = get_all_groups()
    return build_group_tree(groups)


def get_group_by_id(group_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mock_group WHERE id = ?', (group_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_mock_group(group_id, group_data):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    fields = []
    params = []
    allowed_fields = ['name', 'parent_id', 'sort_order', 'icon', 'color']
    
    for field in allowed_fields:
        if field in group_data:
            fields.append(f'{field} = ?')
            params.append(group_data[field])
    
    if fields:
        fields.append('updated_at = ?')
        params.extend([now, group_id])
        cursor.execute(f'UPDATE mock_group SET {", ".join(fields)} WHERE id = ?', params)
        conn.commit()
    
    conn.close()


def delete_mock_group(group_id):
    conn = get_db()
    cursor = conn.cursor()
    
    # 删除子级
    cursor.execute('DELETE FROM mock_group WHERE parent_id = ?', (group_id,))
    
    # 把该目录下的配置移动到根目录
    cursor.execute('UPDATE mock_config SET group_id = 0 WHERE group_id = ?', (group_id,))
    
    # 删除目录
    cursor.execute('DELETE FROM mock_group WHERE id = ?', (group_id,))
    
    conn.commit()
    conn.close()


def get_configs_by_group(group_id, page=1, page_size=10):
    conn = get_db()
    cursor = conn.cursor()
    
    # 构建查询条件
    if group_id == 0:
        where_clauses = ['is_active = 1']
    else:
        where_clauses = ['is_active = 1', 'group_id = ?']
    
    where_query = ' AND '.join(where_clauses)
    params = [group_id] if group_id != 0 else []
    
    # 获取总数
    cursor.execute(f'SELECT COUNT(*) as total FROM mock_config WHERE {where_query}', params)
    total = cursor.fetchone()['total']
    
    # 获取分页数据
    offset = (page - 1) * page_size
    cursor.execute(
        f'SELECT * FROM mock_config WHERE {where_query} ORDER BY id DESC LIMIT ? OFFSET ?',
        params + [page_size, offset]
    )
    rows = cursor.fetchall()
    configs = [dict(row) for row in rows]
    
    # 查询响应
    if configs:
        config_ids = [c['id'] for c in configs]
        placeholders = ','.join('?' for _ in config_ids)
        cursor.execute(f'SELECT * FROM mock_response WHERE config_id IN ({placeholders})', config_ids)
        responses = cursor.fetchall()
        response_dict = {}
        for resp in responses:
            r = dict(resp)
            if r['config_id'] not in response_dict:
                response_dict[r['config_id']] = []
            response_dict[r['config_id']].append(r)
        
        for config in configs:
            config['responses'] = response_dict.get(config['id'], [])
    
    conn.close()
    
    return {
        'items': configs,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size if total > 0 else 1
    }


def init_default_groups():
    """初始化默认目录树"""
    print("开始初始化默认目录...")
    conn = get_db()
    cursor = conn.cursor()
    
    # 检查是否已有目录
    cursor.execute('SELECT COUNT(*) as cnt FROM mock_group')
    cnt = cursor.fetchone()['cnt']
    print(f"当前目录数量: {cnt}")
    
    if cnt == 0:
        print("开始创建默认目录...")
        now = datetime.now().isoformat()
        default_groups = [
            ('用户中心', 0, 1, '👤', '#667eea'),
            ('商品管理', 0, 2, '📦', '#764ba2'),
            ('订单系统', 0, 3, '📋', '#f093fb'),
            ('支付系统', 0, 4, '💰', '#f5576c'),
            ('查询API', 1, 1, '🔍', '#667eea'),
            ('操作API', 1, 2, '⚡', '#764ba2'),
        ]
        
        for name, parent_id, sort_order, icon, color in default_groups:
            print(f"创建目录: {name}")
            cursor.execute('''
                INSERT INTO mock_group (name, parent_id, sort_order, icon, color, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, parent_id, sort_order, icon, color, now, now))
        
        conn.commit()
        print(f'✅ 初始化 {len(default_groups)} 个默认目录')
    else:
        print("目录已存在，跳过初始化")
    
    # 测试获取目录树
    print("测试获取目录树...")
    test_groups = get_all_groups()
    print(f"获取到的目录列表: {test_groups}")
    test_tree = get_group_tree()
    print(f"构建的目录树: {test_tree}")
    
    conn.close()
