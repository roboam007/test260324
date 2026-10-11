# HTTP Mock Server

轻量级HTTP Mock服务，基于Flask + SQLite实现

## 功能特性
- 支持多种请求匹配方式：精确匹配、前缀匹配、正则匹配
- 自定义响应状态码、响应头、响应体
- 支持响应延迟模拟
- 内置配置管理API（增删改查）
- 请求日志记录
- CORS跨域支持

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 初始化示例数据（可选）
```bash
python init_sample_data.py
```

### 3. 启动服务
```bash
python run.py
```
服务默认运行在 http://localhost:5000

## API说明

### 配置管理API（/_api前缀）
- `GET /_api/configs` - 获取所有Mock配置
- `POST /_api/configs` - 创建新的Mock配置
- `GET /_api/configs/<id>` - 获取指定配置
- `PUT /_api/configs/<id>` - 更新配置
- `DELETE /_api/configs/<id>` - 删除配置
- `GET /_api/logs` - 获取请求日志

### 创建Mock配置示例
```json
{
  "name": "获取用户信息",
  "method": "GET",
  "url_pattern": "/api/user/123",
  "url_match_type": "exact",
  "response_status": 200,
  "response_headers": "{\"Content-Type\": \"application/json\"}",
  "response_body": "{\"id\": 123, \"name\": \"张三\"}",
  "response_delay": 100
}
```

## URL匹配类型
- `exact` - 精确匹配（默认）
- `prefix` - 前缀匹配
- `regex` - 正则匹配
