from app.database import init_db, add_mock_config

init_db()
# 添加更多测试数据
for i in range(1, 16):
    add_mock_config({
        'name': f'测试接口 {i}',
        'method': 'GET',
        'url_pattern': f'/api/test/{i}',
        'url_match_type': 'exact',
        'response_status': 200,
        'response_body': f'{{"message": "test {i}"}}',
        'response_delay': 0
    })
print('添加了15条测试数据')
