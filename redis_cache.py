import redis
import json
import hashlib
from typing import Any, Dict
from config import Config
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisCache:
    """Redis缓存操作类"""
    
    def __init__(self):
        """初始化Redis连接"""
        redis_config = Config.get_redis_config()
        self.default_ttl = redis_config["default_ttl_seconds"]
        try:
            self.client = redis.Redis(
                host=redis_config["host"],
                port=redis_config["port"],
                db=redis_config["db"],
                password=redis_config["password"],
                decode_responses=True,  # 自动将响应解码为字符串
                socket_connect_timeout=5  # 连接超时时间
            )
            # 测试连接
            self.client.ping()
            logger.info("成功连接到Redis服务器")
        except redis.exceptions.ConnectionError as e:
            logger.error(f"无法连接到Redis服务器: {e}")
            self.client = None

    def get(self, key: str) -> Any:
        """
        从缓存中获取数据
        
        Args:
            key: 缓存键
            
        Returns:
            Any: 缓存的数据，如果不存在或发生错误则返回None
        """
        if not self.client:
            logger.warning("Redis服务不可用，跳过缓存读取。")
            return None
        
        try:
            cached_data = self.client.get(key)
            if cached_data:
                logger.info(f"缓存命中: {key}")
                return json.loads(cached_data)
            logger.info(f"缓存未命中: {key}")
            return None
        except Exception as e:
            logger.error(f"从Redis获取数据时出错: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = None):
        """
        将数据存入缓存
        
        Args:
            key: 缓存键
            value: 要缓存的数据
            ttl: 缓存时间（秒），如果为None则使用默认值
        """
        if not self.client:
            logger.warning("Redis服务不可用，跳过缓存写入。")
            return
            
        try:
            if ttl is None:
                ttl = self.default_ttl
            
            # 使用json.dumps序列化数据，并处理datetime等特殊类型
            serialized_value = json.dumps(value, default=str)
            self.client.setex(key, ttl, serialized_value)
            logger.info(f"数据已存入缓存: {key}, TTL: {ttl}秒")
        except Exception as e:
            logger.error(f"向Redis存储数据时出错: {e}")

    def generate_cache_key(self, prefix: str, params: Dict[str, Any]) -> str:
        """
        根据参数生成一个稳定的缓存键
        
        Args:
            prefix: 缓存键前缀 (如: "query", "aggregate")
            params: 包含所有查询参数的字典
            
        Returns:
            str: 生成的缓存键
        """
        # 使用json.dumps并对键进行排序，以确保字典顺序不影响最终的哈希值
        params_str = json.dumps(params, sort_keys=True, default=str)
        
        # 使用MD5哈希算法来缩短键的长度，并保持唯一性
        hash_part = hashlib.md5(params_str.encode('utf-8')).hexdigest()
        
        return f"mongodb_api:{prefix}:{hash_part}"

# 创建一个全局的RedisCache实例，方便在应用中复用
redis_cache = RedisCache() 