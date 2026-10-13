import re
import time
import json
import os
import argparse
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from app.database import (
    init_db, migrate_old_data,
    add_mock_config, get_all_mock_configs, get_mock_config_by_id,
    update_mock_config, delete_mock_config, get_mock_configs_paginated,
    add_mock_response, get_responses_by_config_id, get_active_response_by_config_id,
    update_mock_response, delete_mock_response, set_response_active,
    add_request_log, get_recent_logs, get_logs_paginated, clear_logs,
    get_group_tree, add_mock_group, get_all_groups,
    update_mock_group, delete_mock_group, get_configs_by_group,
    init_default_groups
)

app = Flask(__name__)
CORS(app)

def match_config(config, request):
    if config['method'] != request.method:
        return False
    
    url_pattern = config['url_pattern']
    url_match_type = config.get('url_match_type', 'exact')
    
    if url_match_type == 'exact':
        if request.path != url_pattern:
            return False
    elif url_match_type == 'prefix':
        if not request.path.startswith(url_pattern):
            return False
    elif url_match_type == 'regex':
        if not re.fullmatch(url_pattern, request.path):
            return False
    
    return True

def render_mock_template(template_str, request):
    if not template_str:
        return ''
    try:
        data = json.loads(template_str)
        if isinstance(data, dict):
            result = {}
            for k, v in data.items():
                if isinstance(v, str):
                    v = v.replace('{{request.path}}', request.path)
                    v = v.replace('{{request.method}}', request.method)
                result[k] = v
            return json.dumps(result, ensure_ascii=False)
        return template_str
    except:
        return template_str

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/_ui', methods=['GET'])
def ui():
    return render_template('index.html')

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
def mock_handler(path):
    if path.startswith('_ui') or path.startswith('_api'):
        return jsonify({'error': 'Not found'}), 404
        
    configs = get_all_mock_configs()
    matched_config = None
    for config in configs:
        if match_config(config, request):
            matched_config = config
            break
    
    if not matched_config:
        log = {
            'request_method': request.method,
            'request_url': request.url,
            'request_headers': json.dumps(dict(request.headers)),
            'request_query': json.dumps(request.args),
            'request_body': request.get_data(as_text=True),
            'response_status': 404,
            'response_body': json.dumps({'error': 'No mock config matched'}),
            'matched_config_id': None,
            'matched_response_id': None,
            'matched_config_url': None
        }
        add_request_log(log)
        return jsonify({'error': 'No mock config matched'}), 404
    
    response = get_active_response_by_config_id(matched_config['id'])
    if not response:
        log = {
            'request_method': request.method,
            'request_url': request.url,
            'request_headers': json.dumps(dict(request.headers)),
            'request_query': json.dumps(request.args),
            'request_body': request.get_data(as_text=True),
            'response_status': 500,
            'response_body': json.dumps({'error': 'No active response'}),
            'matched_config_id': matched_config['id'],
            'matched_response_id': None,
            'matched_config_url': matched_config['url_pattern']
        }
        add_request_log(log)
        return jsonify({'error': 'No active response'}), 500
    
    delay = response.get('response_delay', 0)
    if delay > 0:
        time.sleep(delay / 1000.0)
    
    status_code = response.get('response_status', 200)
    
    headers = {}
    if response.get('response_headers'):
        try:
            headers = json.loads(response['response_headers'])
        except:
            pass
    
    headers.setdefault('Content-Type', 'application/json')
    
    response_body = render_mock_template(response.get('response_body', ''), request)
    
    log = {
        'request_method': request.method,
        'request_url': request.url,
        'request_headers': json.dumps(dict(request.headers)),
        'request_query': json.dumps(request.args),
        'request_body': request.get_data(as_text=True),
        'response_status': status_code,
        'response_headers': json.dumps(headers),
        'response_body': response_body,
        'response_delay': delay,
        'matched_config_id': matched_config['id'],
        'matched_response_id': response['id'],
        'matched_config_url': matched_config['url_pattern']
    }
    add_request_log(log)
    
    return response_body, status_code, headers

# 配置管理API
@app.route('/_api/configs', methods=['GET'])
def list_configs():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    name = request.args.get('name')
    method = request.args.get('method')
    url_pattern = request.args.get('url')
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    result = get_mock_configs_paginated(page, page_size, name, method, url_pattern, date_start, date_end)
    return jsonify(result)

@app.route('/_api/configs', methods=['POST'])
def create_config():
    data = request.get_json()
    config_id = add_mock_config(data)
    
    if 'responses' in data:
        for resp in data['responses']:
            resp['config_id'] = config_id
            add_mock_response(resp)
    elif 'response_body' in data:
        add_mock_response({
            'config_id': config_id,
            'name': '默认响应',
            'response_status': data.get('response_status', 200),
            'response_headers': data.get('response_headers'),
            'response_body': data.get('response_body'),
            'response_delay': data.get('response_delay', 0),
            'is_active': 1
        })
    
    return jsonify({'id': config_id}), 201

@app.route('/_api/configs/<int:config_id>', methods=['GET'])
def get_config(config_id):
    config = get_mock_config_by_id(config_id)
    if not config:
        return jsonify({'error': 'Config not found'}), 404
    responses = get_responses_by_config_id(config_id)
    config['responses'] = responses
    return jsonify(config)

@app.route('/_api/configs/<int:config_id>', methods=['PUT'])
def update_config_endpoint(config_id):
    data = request.get_json()
    update_mock_config(config_id, data)
    return jsonify({'status': 'ok'})

@app.route('/_api/configs/<int:config_id>', methods=['DELETE'])
def delete_config_endpoint(config_id):
    delete_mock_config(config_id)
    return jsonify({'status': 'ok'})

# 响应管理API
@app.route('/_api/configs/<int:config_id>/responses', methods=['GET'])
def list_responses(config_id):
    responses = get_responses_by_config_id(config_id)
    return jsonify(responses)

@app.route('/_api/configs/<int:config_id>/responses', methods=['POST'])
def create_response(config_id):
    data = request.get_json()
    data['config_id'] = config_id
    response_id = add_mock_response(data)
    return jsonify({'id': response_id}), 201

@app.route('/_api/responses/<int:response_id>', methods=['PUT'])
def update_response_endpoint(response_id):
    data = request.get_json()
    update_mock_response(response_id, data)
    return jsonify({'status': 'ok'})

@app.route('/_api/responses/<int:response_id>', methods=['DELETE'])
def delete_response_endpoint(response_id):
    delete_mock_response(response_id)
    return jsonify({'status': 'ok'})

@app.route('/_api/responses/<int:response_id>/active', methods=['POST'])
def set_active_endpoint(response_id):
    data = request.get_json()
    is_active = data.get('is_active', True)
    set_response_active(response_id, is_active)
    return jsonify({'status': 'ok'})

# 日志API
@app.route('/_api/logs', methods=['GET'])
def list_logs():
    page = request.args.get('page', None, type=int)
    page_size = request.args.get('page_size', None, type=int)
    url = request.args.get('url')
    mock_url = request.args.get('mock_url')
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    # 如果提供了分页参数，返回分页数据
    if page is not None or page_size is not None:
        page = page or 1
        page_size = page_size or 10
        result = get_logs_paginated(page, page_size, url, mock_url, date_start, date_end)
        return jsonify(result)
    # 否则返回旧格式（limit参数）
    limit = request.args.get('limit', 50, type=int)
    logs = get_recent_logs(limit)
    return jsonify(logs)

@app.route('/_api/logs', methods=['DELETE'])
def clear_logs_endpoint():
    clear_logs()
    return jsonify({'status': 'ok'})

# ==================== 目录树API ====================
@app.route('/_api/groups', methods=['GET'])
def get_groups():
    return jsonify(get_all_groups())

@app.route('/_api/groups', methods=['POST'])
def create_group():
    data = request.get_json()
    group_id = add_mock_group(data)
    return jsonify({'id': group_id}), 201

@app.route('/_api/groups/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    data = request.get_json()
    update_mock_group(group_id, data)
    return jsonify({'status': 'ok'})

@app.route('/_api/groups/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    delete_mock_group(group_id)
    return jsonify({'status': 'ok'})

# 按目录获取配置列表
@app.route('/_api/groups/<int:group_id>/configs', methods=['GET'])
def get_configs_by_group_id(group_id):
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    name = request.args.get('name')
    method = request.args.get('method')
    url_pattern = request.args.get('url')
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    
    # 有筛选条件时使用原有的通用接口
    if name or method or url_pattern or date_start or date_end:
        result = get_mock_configs_paginated(page, page_size, name, method, url_pattern, date_start, date_end)
        # 筛选 group_id
        if group_id != 0:
            result['items'] = [c for c in result['items'] if c.get('group_id', 0) == group_id]
    else:
        result = get_configs_by_group(group_id, page, page_size)
    
    return jsonify(result)

if __name__ == '__main__':
    init_db()
    migrate_old_data()
    # 先确保表结构没问题，再初始化默认目录
    try:
        init_default_groups()
    except Exception as e:
        print(f"初始化默认目录失败: {e}")
    
    parser = argparse.ArgumentParser(description='HTTP Mock Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen (default: 5000)')
    parser.add_argument('--https', action='store_true', help='Enable HTTPS with adhoc certificate')
    args = parser.parse_args()
    
    ssl_context = None
    if args.https:
        ssl_context = 'adhoc'
        print(f"🔒 HTTPS enabled: {args.host}:{args.port} (adhoc cert)")
    else:
        print(f"🌐 HTTP enabled: {args.host}:{args.port}")
    
    app.run(host=args.host, port=args.port, ssl_context=ssl_context, debug=True)
