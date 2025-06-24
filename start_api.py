#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB API 启动脚本
提供多种启动选项和配置
"""

import uvicorn
import argparse
import sys
import os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="MongoDB查询API启动脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python start_api.py                    # 默认配置启动
  python start_api.py --host 0.0.0.0     # 指定主机
  python start_api.py --port 8080        # 指定端口
  python start_api.py --reload           # 开发模式（自动重载）
  python start_api.py --workers 4        # 生产模式（多进程）
  python start_api.py --log-level debug  # 调试模式
        """
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="监听主机地址 (默认: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="监听端口 (默认: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="开发模式：启用自动重载"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="生产模式：工作进程数量 (默认: 1)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
        help="日志级别 (默认: info)"
    )
    
    parser.add_argument(
        "--config",
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="MongoDB查询API v1.0.0"
    )
    
    args = parser.parse_args()
    
    # 检查依赖
    try:
        import fastapi
        import pymongo
        import uvicorn
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)
    
    # 显示启动信息
    print("🚀 MongoDB查询API启动中...")
    print(f"📍 主机: {args.host}")
    print(f"🔌 端口: {args.port}")
    print(f"📝 日志级别: {args.log_level}")
    
    if args.reload:
        print("🔄 开发模式: 自动重载已启用")
    elif args.workers > 1:
        print(f"⚡ 生产模式: {args.workers} 个工作进程")
    
    print(f"🌐 Swagger文档: http://{args.host}:{args.port}/docs")
    print(f"📖 ReDoc文档: http://{args.host}:{args.port}/redoc")
    print(f"❤️  健康检查: http://{args.host}:{args.port}/health")
    print("-" * 50)
    
    # 启动配置
    config = uvicorn.Config(
        "fastapi_mongodb:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
        access_log=True,
        use_colors=True
    )
    
    # 创建服务器
    server = uvicorn.Server(config)
    
    try:
        # 启动服务器
        server.run()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ Python版本过低，需要Python 3.7+")
        return False
    
    print(f"✅ Python版本: {sys.version}")
    
    # 检查必要文件
    required_files = [
        "fastapi_mongodb.py",
        "mongodb_api.py",
        "swagger_config.py"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ 缺少文件: {file}")
            return False
    
    print("✅ 所有必要文件存在")
    
    # 检查依赖
    try:
        import fastapi
        import pymongo
        import uvicorn
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    # 启动服务
    main() 