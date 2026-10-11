from app.database import init_db, add_mock_config, add_mock_response

# 初始化数据库
init_db()
print("数据库初始化完成！")

# 示例1：获取用户信息
print("\n正在添加示例1：获取用户信息...")
config1_id = add_mock_config({
    "name": "获取用户信息",
    "method": "GET",
    "url_pattern": "/api/user/123",
    "url_match_type": "exact"
})
# 添加2个响应
add_mock_response({
    "config_id": config1_id,
    "name": "成功响应",
    "response_status": 200,
    "response_body": '{"id": 123, "name": "张三", "email": "zhangsan@example.com", "role": "admin"}',
    "is_active": 1
})
add_mock_response({
    "config_id": config1_id,
    "name": "失败响应-用户不存在",
    "response_status": 404,
    "response_body": '{"error": "User not found", "code": 404}'
})

# 示例2：创建订单
print("正在添加示例2：创建订单...")
config2_id = add_mock_config({
    "name": "创建订单",
    "method": "POST",
    "url_pattern": "/api/orders",
    "url_match_type": "exact"
})
add_mock_response({
    "config_id": config2_id,
    "name": "创建成功",
    "response_status": 201,
    "response_body": '{"order_id": "ORD-2024-1001", "status": "created", "total": 299.00}',
    "response_delay": 500,
    "is_active": 1
})
add_mock_response({
    "config_id": config2_id,
    "name": "参数错误",
    "response_status": 400,
    "response_body": '{"error": "Invalid parameters", "details": "Missing product_id"}'
})

# 示例3：产品列表（前缀匹配）
print("正在添加示例3：产品列表...")
config3_id = add_mock_config({
    "name": "产品列表",
    "method": "GET",
    "url_pattern": "/api/products",
    "url_match_type": "prefix"
})
add_mock_response({
    "config_id": config3_id,
    "name": "产品列表响应",
    "response_status": 200,
    "response_body": '{"total": 2, "items": [{"id": 1, "name": "iPhone 15", "price": 5999}, {"id": 2, "name": "MacBook Pro", "price": 12999}]}',
    "is_active": 1
})

print("\n✅ 示例数据添加完成！")
print("\n已添加的示例：")
print("  1. GET /api/user/123 - 获取用户信息（2个响应）")
print("  2. POST /api/orders - 创建订单（2个响应）")
print("  3. GET /api/products - 产品列表（前缀匹配）")
