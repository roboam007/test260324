import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.database import add_mock_config, add_mock_response, init_db

def add_test_data():
    init_db()
    
    # 10条测试配置
    test_configs = [
        {
            'name': '用户详情接口',
            'method': 'GET',
            'url_pattern': '/api/user/1',
            'url_match_type': 'exact',
            'response': {
                'name': '成功响应',
                'response_status': 200,
                'response_body': '{"id": 1, "name": "张三", "email": "zhangsan@example.com"}'
            }
        },
        {
            'name': '用户列表接口',
            'method': 'GET',
            'url_pattern': '/api/users',
            'url_match_type': 'exact',
            'response': {
                'name': '用户列表',
                'response_status': 200,
                'response_body': '{"users": [{"id": 1, "name": "张三"}, {"id": 2, "name": "李四"}], "total": 2}'
            }
        },
        {
            'name': '创建用户接口',
            'method': 'POST',
            'url_pattern': '/api/users',
            'url_match_type': 'exact',
            'response': {
                'name': '创建成功',
                'response_status': 201,
                'response_body': '{"id": 3, "name": "王五", "status": "created"}'
            }
        },
        {
            'name': '更新用户接口',
            'method': 'PUT',
            'url_pattern': '/api/user/1',
            'url_match_type': 'exact',
            'response': {
                'name': '更新成功',
                'response_status': 200,
                'response_body': '{"id": 1, "name": "张三", "email": "updated@example.com", "status": "updated"}'
            }
        },
        {
            'name': '删除用户接口',
            'method': 'DELETE',
            'url_pattern': '/api/user/1',
            'url_match_type': 'exact',
            'response': {
                'name': '删除成功',
                'response_status': 200,
                'response_body': '{"status": "deleted"}'
            }
        },
        {
            'name': '商品列表接口',
            'method': 'GET',
            'url_pattern': '/api/products',
            'url_match_type': 'exact',
            'response': {
                'name': '商品列表',
                'response_status': 200,
                'response_body': '{"products": [{"id": 1, "name": "iPhone", "price": 9999}, {"id": 2, "name": "MacBook", "price": 14999}], "total": 2}'
            }
        },
        {
            'name': '订单查询接口',
            'method': 'GET',
            'url_pattern': '/api/orders',
            'url_match_type': 'prefix',
            'response': {
                'name': '订单列表',
                'response_status': 200,
                'response_body': '{"orders": [{"id": 1, "status": "paid", "amount": 9999}, {"id": 2, "status": "shipped", "amount": 14999}], "total": 2}'
            }
        },
        {
            'name': '登录接口',
            'method': 'POST',
            'url_pattern': '/api/login',
            'url_match_type': 'exact',
            'response': {
                'name': '登录成功',
                'response_status': 200,
                'response_body': '{"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "user_id": 1}'
            }
        },
        {
            'name': '健康检查接口',
            'method': 'GET',
            'url_pattern': '/health',
            'url_match_type': 'exact',
            'response': {
                'name': '健康状态',
                'response_status': 200,
                'response_body': '{"status": "ok", "timestamp": 1699999999}'
            }
        },
        {
            'name': '404接口',
            'method': 'GET',
            'url_pattern': '/api/404',
            'url_match_type': 'exact',
            'response': {
                'name': '未找到',
                'response_status': 404,
                'response_body': '{"error": "Not Found", "message": "The requested resource was not found"}'
            }
        }
    ]
    
    for config_data in test_configs:
        config_id = add_mock_config({
            'name': config_data['name'],
            'method': config_data['method'],
            'url_pattern': config_data['url_pattern'],
            'url_match_type': config_data['url_match_type']
        })
        
        response = config_data['response']
        response_id = add_mock_response({
            'config_id': config_id,
            'name': response['name'],
            'response_status': response['response_status'],
            'response_body': response['response_body'],
            'is_active': 1
        })
        
        print(f"添加配置: {config_data['name']} (ID: {config_id}) -> 响应ID: {response_id}")
    
    print(f"✅ 成功添加 {len(test_configs)} 条测试配置！")

if __name__ == '__main__':
    add_test_data()
