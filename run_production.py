"""
生产环境启动脚本 - 使用Waitress WSGI服务器
适用于Windows生产环境部署
"""
import argparse
from app.main import app, init_db, migrate_old_data, init_default_groups


def main():
    # 初始化数据库
    init_db()
    migrate_old_data()
    
    # 初始化默认目录
    try:
        init_default_groups()
    except Exception as e:
        print(f"初始化默认目录失败: {e}")
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='HTTP Mock Server (Production)')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen (default: 5000)')
    parser.add_argument('--threads', type=int, default=4, help='Number of worker threads (default: 4)')
    args = parser.parse_args()
    
    try:
        from waitress import serve
        print(f"🚀 启动生产服务器: http://{args.host}:{args.port}")
        print(f"📊 工作线程数: {args.threads}")
        print("⚠️  注意: Waitress不支持HTTPS，如需HTTPS请使用反向代理（如Nginx）")
        serve(
            app,
            host=args.host,
            port=args.port,
            threads=args.threads,
            url_prefix='',
            ident='HTTP Mock Server'
        )
    except ImportError:
        print("❌ 错误: Waitress未安装")
        print("请运行: pip install waitress")
        print("\n或者使用开发服务器（仅用于开发）:")
        print("python run.py")


if __name__ == '__main__':
    main()
