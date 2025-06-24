#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB查询接口配置文件
"""

import os
from typing import Dict, Any

class Config:
    """配置类"""
    
    # MongoDB默认连接配置
    MONGODB_CONFIG = {
        "default": {
            "connection_string": os.getenv("MONGODB_URI", "mongodb://localhost:27017/"),
            "database_name": os.getenv("MONGODB_DATABASE", "test_db"),
            "collection_name": os.getenv("MONGODB_COLLECTION", "users"),
            "server_selection_timeout_ms": 5000,
            "connect_timeout_ms": 10000,
            "socket_timeout_ms": 10000,
            "max_pool_size": 10,
            "min_pool_size": 1
        },
        
        # 开发环境配置
        "development": {
            "connection_string": "mongodb://localhost:27017/",
            "database_name": "dev_db",
            "collection_name": "users",
            "server_selection_timeout_ms": 5000,
            "connect_timeout_ms": 10000,
            "socket_timeout_ms": 10000,
            "max_pool_size": 5,
            "min_pool_size": 1
        },
        
        # 生产环境配置
        "production": {
            "connection_string": os.getenv("MONGODB_URI", "mongodb://localhost:27017/"),
            "database_name": os.getenv("MONGODB_DATABASE", "prod_db"),
            "collection_name": os.getenv("MONGODB_COLLECTION", "users"),
            "server_selection_timeout_ms": 10000,
            "connect_timeout_ms": 20000,
            "socket_timeout_ms": 20000,
            "max_pool_size": 20,
            "min_pool_size": 5
        }
    }
    
    # Redis缓存配置
    REDIS_CONFIG = {
        "host": os.getenv("REDIS_HOST", "127.0.0.1"),
        "port": int(os.getenv("REDIS_PORT", 31337)),
        "db": int(os.getenv("REDIS_DB", 9)),
        "password": os.getenv("REDIS_PASSWORD", 'lobbyredisLock527788'),
        "default_ttl_seconds": 86400,  # 默认缓存时间24小时 (24 * 60 * 60)
    }
    
    # API配置
    API_CONFIG = {
        "host": os.getenv("API_HOST", "0.0.0.0"),
        "port": int(os.getenv("API_PORT", "8000")),
        "debug": os.getenv("API_DEBUG", "False").lower() == "true",
        "reload": os.getenv("API_RELOAD", "True").lower() == "true",
        "log_level": os.getenv("API_LOG_LEVEL", "info")
    }
    
    # 日志配置
    LOGGING_CONFIG = {
        "level": os.getenv("LOG_LEVEL", "INFO"),
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": os.getenv("LOG_FILE", "mongodb_api.log")
    }
    
    # 查询配置
    QUERY_CONFIG = {
        "default_limit": 100,
        "max_limit": 1000,
        "default_skip": 0,
        "max_skip": 10000,
        "timeout_seconds": 30
    }
    
    @classmethod
    def get_mongodb_config(cls, environment: str = "default") -> Dict[str, Any]:
        """
        获取MongoDB配置
        
        Args:
            environment: 环境名称 (default, development, production)
            
        Returns:
            Dict: MongoDB配置字典
        """
        return cls.MONGODB_CONFIG.get(environment, cls.MONGODB_CONFIG["default"])
    
    @classmethod
    def get_redis_config(cls) -> Dict[str, Any]:
        """
        获取Redis配置
        
        Returns:
            Dict: Redis配置字典
        """
        return cls.REDIS_CONFIG
    
    @classmethod
    def get_api_config(cls) -> Dict[str, Any]:
        """
        获取API配置
        
        Returns:
            Dict: API配置字典
        """
        return cls.API_CONFIG
    
    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """
        获取日志配置
        
        Returns:
            Dict: 日志配置字典
        """
        return cls.LOGGING_CONFIG
    
    @classmethod
    def get_query_config(cls) -> Dict[str, Any]:
        """
        获取查询配置
        
        Returns:
            Dict: 查询配置字典
        """
        return cls.QUERY_CONFIG
    
    @classmethod
    def validate_connection_string(cls, connection_string: str) -> bool:
        """
        验证MongoDB连接字符串格式
        
        Args:
            connection_string: 连接字符串
            
        Returns:
            bool: 是否有效
        """
        if not connection_string:
            return False
        
        # 基本格式检查
        if not connection_string.startswith("mongodb://") and not connection_string.startswith("mongodb+srv://"):
            return False
        
        return True
    
    @classmethod
    def get_environment(cls) -> str:
        """
        获取当前环境
        
        Returns:
            str: 环境名称
        """
        return os.getenv("ENVIRONMENT", "default")


# 使用示例
if __name__ == "__main__":
    # 获取默认配置
    default_config = Config.get_mongodb_config()
    print("默认MongoDB配置:")
    print(f"  连接字符串: {default_config['connection_string']}")
    print(f"  数据库: {default_config['database_name']}")
    print(f"  集合: {default_config['collection_name']}")
    
    # 获取开发环境配置
    dev_config = Config.get_mongodb_config("development")
    print("\n开发环境MongoDB配置:")
    print(f"  连接字符串: {dev_config['connection_string']}")
    print(f"  数据库: {dev_config['database_name']}")
    print(f"  集合: {dev_config['collection_name']}")
    
    # 获取Redis配置
    redis_config = Config.get_redis_config()
    print("\nRedis配置:")
    print(f"  主机: {redis_config['host']}")
    print(f"  端口: {redis_config['port']}")
    print(f"  默认TTL: {redis_config['default_ttl_seconds']}秒 ({redis_config['default_ttl_seconds'] / 3600}小时)")
    
    # 获取API配置
    api_config = Config.get_api_config()
    print("\nAPI配置:")
    print(f"  主机: {api_config['host']}")
    print(f"  端口: {api_config['port']}")
    print(f"  调试模式: {api_config['debug']}")
    
    # 验证连接字符串
    test_connection = "mongodb://localhost:27017/"
    is_valid = Config.validate_connection_string(test_connection)
    print(f"\n连接字符串验证: {test_connection} -> {'有效' if is_valid else '无效'}") 