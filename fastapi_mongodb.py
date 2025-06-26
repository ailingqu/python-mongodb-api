from fastapi import FastAPI, HTTPException, Depends, Query, Path, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_serializer
from typing import Dict, List, Any, Optional
from mongodb_api import MongoDBQueryAPI
from redis_cache import redis_cache
import uvicorn
from contextlib import asynccontextmanager
from datetime import datetime
from swagger_config import get_swagger_config
import time
import json
from fastapi.responses import Response

# 获取Swagger配置
swagger_config = get_swagger_config()

# 全局MongoDB API实例
mongodb_api = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global mongodb_api
    mongodb_api = MongoDBQueryAPI()
    yield
    if mongodb_api:
        mongodb_api.close_connection()

# 创建FastAPI应用，使用优化的Swagger配置
app = FastAPI(
    title="MongoDB查询API",
    description="""
## MongoDB查询接口

这是一个完整的MongoDB查询接口，支持各种查询操作。

### 主要功能
- 🔌 **连接管理** - 灵活的MongoDB连接配置
- 🔍 **文档查询** - 支持简单和复杂条件查询
- 📊 **聚合查询** - 强大的数据聚合功能
- 📈 **统计信息** - 获取集合详细统计
- 🛡️ **错误处理** - 完善的异常处理机制

### 使用流程
1. 使用 `/query` 接口，传入连接信息和查询条件
2. 使用 `/aggregate` 接口进行聚合查询
3. 可选调用 `/stats` 获取统计信息

### 环境要求
- Python 3.7+
- MongoDB 4.0+
- pymongo 4.0+

### 示例连接字符串
- 本地连接: `mongodb://localhost:27017/`
- 带认证: `mongodb://username:password@localhost:27017/`
- 集群连接: `mongodb://host1:port1,host2:port2/`

### 快速开始
1. 启动服务后访问 `/docs` 查看Swagger文档
2. 使用"Try it out"功能直接测试API
3. 查看示例代码了解使用方法
    """,
    version="1.0.0",
    contact={
        "name": "MongoDB API Support",
        "email": "support@example.com",
        "url": "https://github.com/your-repo/mongodb-api"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    # 使用优化的Swagger UI配置
    swagger_ui_parameters=swagger_config["swagger_ui_parameters"],
    # 添加服务器配置
    servers=swagger_config["servers"],
    # 添加标签配置
    openapi_tags=swagger_config["tags"]
)

# ⚡️就在这里添加！
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    添加性能统计中间件
    - 计算请求处理时间
    - 计算响应数据长度
    - 添加到响应头和日志
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # 将处理时间添加到响应头
    response.headers["X-Process-Time-Ms"] = str(round(process_time * 1000, 2))
    
    # 获取响应体并计算长度
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk
    
    response_length = len(response_body)
    response.headers["X-Response-Length"] = str(response_length)
    
    # 打印日志
    print(f"INFO:     Request: {request.method} {request.url.path} - "
          f"Process Time: {response.headers['X-Process-Time-Ms']}ms - "
          f"Response Length: {response_length} bytes")

    # 从原始响应重新创建新的响应，因为body_iterator已被消耗
    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )

# 数据模型
class ConnectionRequest(BaseModel):
    connection_string: str = Field(
        ..., 
        description="MongoDB连接字符串",
        example="mongodb://localhost:27017/",
        min_length=1
    )
    database_name: str = Field(
        ..., 
        description="数据库名称",
        example="test_db",
        min_length=1
    )
    collection_name: str = Field(
        ..., 
        description="集合名称",
        example="users",
        min_length=1
    )

    class Config:
        json_schema_extra = {
            "example": {
                "connection_string": "mongodb://localhost:27017/",
                "database_name": "test_db",
                "collection_name": "users"
            }
        }

class QueryRequest(BaseModel):
    # 数据库连接信息
    connection_string: str = Field(
        ..., 
        description="MongoDB连接字符串",
        example="mongodb://localhost:27017/",
        min_length=1
    )
    database_name: str = Field(
        ..., 
        description="数据库名称",
        example="test_db",
        min_length=1
    )
    collection_name: str = Field(
        ..., 
        description="集合名称",
        example="users",
        min_length=1
    )
    
    # 查询参数
    query_filter: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="查询条件，支持MongoDB查询语法",
        example={"age": {"$gte": 25}, "status": "active"}
    )
    projection: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="投影字段，1表示包含，0表示排除",
        example={"name": 1, "age": 1, "email": 1, "_id": 0}
    )
    sort: Optional[List[List[Any]]] = Field(
        default=None, 
        description="排序条件，格式：[['字段名', 1或-1]]，1为升序，-1为降序",
        example=[["age", -1], ["name", 1]]
    )
    limit: Optional[int] = Field(
        default=None, 
        description="限制返回文档数量",
        example=10,
        ge=1,
        le=1000
    )
    skip: Optional[int] = Field(
        default=None, 
        description="跳过文档数量",
        example=0,
        ge=0,
        le=10000
    )
    cache_ttl: Optional[int] = Field(
        default=300,
        description="缓存时间（秒）。传0则不使用缓存，传None则使用默认缓存时间。"
    )
    force_refresh: bool = Field(
        default=False,
        description="是否强制从数据库重新获取数据，忽略缓存。如果为true，将直接查询数据库并更新缓存。"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "connection_string": "mongodb://localhost:27017/",
                "database_name": "test_db",
                "collection_name": "users",
                "query_filter": {
                    "age": {"$gte": 25},
                    "department": {"$in": ["技术部", "销售部"]},
                    "status": "active"
                },
                "projection": {
                    "name": 1,
                    "age": 1,
                    "email": 1,
                    "department": 1,
                    "_id": 0
                },
                "sort": [["age", -1], ["name", 1]],
                "limit": 10,
                "skip": 0
            }
        }

class QueryOneRequest(BaseModel):
    # 数据库连接信息
    connection_string: str = Field(
        ..., 
        description="MongoDB连接字符串",
        example="mongodb://localhost:27017/",
        min_length=1
    )
    database_name: str = Field(
        ..., 
        description="数据库名称",
        example="test_db",
        min_length=1
    )
    collection_name: str = Field(
        ..., 
        description="集合名称",
        example="users",
        min_length=1
    )
    
    # 查询参数
    query_filter: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="查询条件，支持MongoDB查询语法",
        example={"age": {"$gte": 25}, "status": "active"}
    )
    projection: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="投影字段，1表示包含，0表示排除",
        example={"name": 1, "age": 1, "email": 1, "_id": 0}
    )
    sort: Optional[List[List[Any]]] = Field(
        default=None, 
        description="排序条件，格式：[['字段名', 1或-1]]，1为升序，-1为降序",
        example=[["age", -1], ["name", 1]]
    )
    cache_ttl: Optional[int] = Field(
        default=300,
        description="缓存时间（秒）。传0则不使用缓存，传None则使用默认缓存时间。"
    )
    force_refresh: bool = Field(
        default=False,
        description="是否强制从数据库重新获取数据，忽略缓存。如果为true，将直接查询数据库并更新缓存。"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "connection_string": "mongodb://localhost:27017/",
                "database_name": "test_db",
                "collection_name": "users",
                "query_filter": {
                    "age": {"$gte": 25},
                    "department": {"$in": ["技术部", "销售部"]},
                    "status": "active"
                },
                "projection": {
                    "name": 1,
                    "age": 1,
                    "email": 1,
                    "department": 1,
                    "_id": 0
                },
                "sort": [["age", -1], ["name", 1]]
            }
        }

class AggregateRequest(BaseModel):
    # 数据库连接信息
    connection_string: str = Field(
        ..., 
        description="MongoDB连接字符串",
        example="mongodb://localhost:27017/",
        min_length=1
    )
    database_name: str = Field(
        ..., 
        description="数据库名称",
        example="test_db",
        min_length=1
    )
    collection_name: str = Field(
        ..., 
        description="集合名称",
        example="users",
        min_length=1
    )
    
    # 聚合参数
    pipeline: List[Dict[str, Any]] = Field(
        ..., 
        description="聚合管道，支持MongoDB聚合操作符",
        min_items=1
    )
    cache_ttl: Optional[int] = Field(
        default=300,
        description="缓存时间（秒）。传0则不使用缓存，传None则使用默认缓存时间。"
    )
    force_refresh: bool = Field(
        default=False,
        description="是否强制从数据库重新获取数据，忽略缓存。如果为true，将直接查询数据库并更新缓存。"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "connection_string": "mongodb://localhost:27017/",
                "database_name": "test_db",
                "collection_name": "users",
                "pipeline": [
                    {"$match": {"age": {"$gte": 25}}},
                    {"$group": {"_id": "$department", "count": {"$sum": 1}, "avg_age": {"$avg": "$age"}}},
                    {"$sort": {"count": -1}}
                ]
            }
        }

class DistinctRequest(BaseModel):
    # 数据库连接信息
    connection_string: str = Field(
        ..., 
        description="MongoDB连接字符串",
        example="mongodb://localhost:27017/",
        min_length=1
    )
    database_name: str = Field(
        ..., 
        description="数据库名称",
        example="test_db",
        min_length=1
    )
    collection_name: str = Field(
        ..., 
        description="集合名称",
        example="users",
        min_length=1
    )
    
    # distinct参数
    field: str = Field(
        ..., 
        description="要查询唯一值的字段名",
        example="department",
        min_length=1
    )
    query_filter: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="可选的查询条件，用于过滤文档",
        example={"age": {"$gte": 25}, "status": "active"}
    )
    cache_ttl: Optional[int] = Field(
        default=300,
        description="缓存时间（秒）。传0则不使用缓存，传None则使用默认缓存时间。"
    )
    force_refresh: bool = Field(
        default=False,
        description="是否强制从数据库重新获取数据，忽略缓存。如果为true，将直接查询数据库并更新缓存。"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "connection_string": "mongodb://localhost:27017/",
                "database_name": "test_db",
                "collection_name": "users",
                "field": "department",
                "query_filter": {"age": {"$gte": 25}},
                "cache_ttl": 300
            }
        }

class ApiResponse(BaseModel):
    status: str = Field(..., description="响应状态：success/error/info")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    count: Optional[int] = Field(default=None, description="数据条数")
    cache_ttl: Optional[int] = Field(default=None, description="缓存时间（秒）")
    timestamp: str = Field(..., description="响应时间戳")

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        """自定义模型序列化，仅在count不为None时返回该字段"""
        response = {
            "status": self.status,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp,
        }
        if self.count is not None:
            response['count'] = self.count
        if self.cache_ttl is not None:
            response['cache_ttl'] = self.cache_ttl
        return response

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "查询成功，返回 5 个文档",
                "data": [
                    {"name": "张三", "age": 28, "email": "zhangsan@example.com"},
                    {"name": "李四", "age": 32, "email": "lisi@example.com"}
                ],
                "count": 5,
                "timestamp": "2024-01-01T12:00:00"
            }
        }

# 依赖函数
def get_mongodb_api():
    """获取MongoDB API实例"""
    if mongodb_api is None:
        raise HTTPException(status_code=500, detail="MongoDB API未初始化")
    return mongodb_api

# API路由
@app.post(
    "/connect", 
    response_model=ApiResponse,
    summary="连接MongoDB数据库",
    description="""
    连接到指定的MongoDB数据库和集合。
    
    **参数说明：**
    - `connection_string`: MongoDB连接字符串
    - `database_name`: 要连接的数据库名称
    - `collection_name`: 要操作的集合名称
    
    **返回结果：**
    - 成功：返回连接成功信息
    - 失败：返回错误详情
    
    **使用示例：**
    ```json
    {
        "connection_string": "mongodb://localhost:27017/",
        "database_name": "test_db",
        "collection_name": "users"
    }
    ```
    """,
    tags=["连接管理"],
    responses={
        200: {
            "description": "连接成功",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "连接成功",
                        "data": {
                            "database": "test_db",
                            "collection": "users"
                        },
                        "timestamp": "2024-01-01T12:00:00"
                    }
                }
            }
        },
        400: {
            "description": "连接失败",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "连接失败: 无法连接到MongoDB服务器",
                        "timestamp": "2024-01-01T12:00:00"
                    }
                }
            }
        }
    }
)
async def connect_to_mongodb(
    request: ConnectionRequest,
    api: MongoDBQueryAPI = Depends(get_mongodb_api)
): 
    result = api.connect_to_mongodb(
        request.connection_string,
        request.database_name,
        request.collection_name
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return ApiResponse(**result)

@app.post(
    "/query", 
    response_model=ApiResponse,
    summary="查询MongoDB文档（自动连接和断开）",
    description="""
    根据指定条件查询MongoDB文档，自动处理连接和断开。
    
    **功能特点：**
    - 自动连接指定的MongoDB数据库
    - 执行查询操作
    - 自动断开连接，释放资源
    - 支持所有MongoDB查询功能
    
    **查询条件示例：**
    - 简单条件：`{"age": 25}`
    - 范围查询：`{"age": {"$gte": 20, "$lte": 30}}`
    - 数组查询：`{"department": {"$in": ["技术部", "销售部"]}}`
    - 复杂条件：`{"$and": [{"age": {"$gte": 25}}, {"status": "active"}]}`
    
    **投影字段说明：**
    - `{"field": 1}` - 包含该字段
    - `{"field": 0}` - 排除该字段
    - `{"_id": 0}` - 排除_id字段
    
    **排序说明：**
    - `[["field", 1]]` - 按字段升序
    - `[["field", -1]]` - 按字段降序
    - `[["field1", 1], ["field2", -1]]` - 多字段排序
    """,
    tags=["数据查询"],
    responses={
        200: {
            "description": "查询成功",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "查询成功，返回 3 个文档",
                        "data": [
                            {"name": "张三", "age": 28, "email": "zhangsan@example.com"},
                            {"name": "李四", "age": 32, "email": "lisi@example.com"},
                            {"name": "王五", "age": 25, "email": "wangwu@example.com"}
                        ],
                        "count": 3,
                        "timestamp": "2024-01-01T12:00:00"
                    }
                }
            }
        },
        400: {
            "description": "查询失败",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "查询失败: 无法连接到MongoDB服务器",
                        "timestamp": "2024-01-01T12:00:00"
                    }
                }
            }
        }
    }
)
async def query_documents(
    request: QueryRequest
):
    """
    查询MongoDB文档，自动处理连接和断开
    """
    cache_key = None
    use_cache = request.cache_ttl != 0

    # 1. 检查缓存 (如果不强制刷新)
    if use_cache and not request.force_refresh:
        # 使用请求的所有参数来生成缓存键，确保唯一性
        cache_key = redis_cache.generate_cache_key("query", request.dict())
        cached_result = redis_cache.get(cache_key)
        if cached_result:
            # 如果命中缓存，直接返回结果，不创建MongoDB连接
            cached_result["message"] = f"查询成功 (来自缓存)，返回 {cached_result.get('count', 0)} 个文档"
            # 添加缓存时间信息
            cached_result["cache_ttl"] = request.cache_ttl
            return ApiResponse(**cached_result)

    # 2. 只有缓存未命中时才创建MongoDB连接和查询
    api = MongoDBQueryAPI()
    
    try:
        # 连接数据库
        connection_result = api.connect_to_mongodb(
            request.connection_string,
            request.database_name,
            request.collection_name
        )
        
        if connection_result["status"] == "error":
            return ApiResponse(
                status="error",
                message=f"连接失败: {connection_result['message']}",
                timestamp=datetime.now().isoformat()
            )
        
        # 转换排序格式
        sort_list = None
        if request.sort:
            sort_list = [(item[0], item[1]) for item in request.sort]
        
        # 执行查询
        result = api.query_documents(
            query_filter=request.query_filter,
            projection=request.projection,
            sort=sort_list,
            limit=request.limit,
            skip=request.skip
        )
        
        # 3. 设置缓存 (如果查询成功且启用了缓存)
        if use_cache and result["status"] == "success":
            if cache_key is None: # 如果是强制刷新，之前没生成key
                cache_key = redis_cache.generate_cache_key("query", request.dict())
            redis_cache.set(cache_key, result, ttl=request.cache_ttl)
            # 添加缓存时间信息到响应
            result["cache_ttl"] = request.cache_ttl

        return ApiResponse(**result)
        
    except Exception as e:
        return ApiResponse(
            status="error",
            message=f"查询过程中发生错误: {str(e)}",
            timestamp=datetime.now().isoformat()
        )
    finally:
        # 确保连接被关闭
        api.close_connection()

@app.post(
    "/query_one", 
    response_model=ApiResponse,
    summary="查询MongoDB单个文档（自动连接和断开）",
    description="""
    根据指定条件查询MongoDB单个文档，自动处理连接和断开。
    
    **功能特点：**
    - 自动连接指定的MongoDB数据库
    - 执行查询操作，只返回第一个匹配的文档
    - 自动断开连接，释放资源
    - 支持所有MongoDB查询功能
    
    **使用场景：**
    - 根据唯一ID查询单个文档
    - 获取满足条件的第一个文档
    - 检查文档是否存在
    - 获取最新或最旧的文档
    
    **查询条件示例：**
    - 简单条件：`{"age": 25}`
    - 范围查询：`{"age": {"$gte": 20, "$lte": 30}}`
    - 数组查询：`{"department": {"$in": ["技术部", "销售部"]}}`
    - 复杂条件：`{"$and": [{"age": {"$gte": 25}}, {"status": "active"}]}`
    
    **投影字段说明：**
    - `{"field": 1}` - 包含该字段
    - `{"field": 0}` - 排除该字段
    - `{"_id": 0}` - 排除_id字段
    
    **排序说明：**
    - `[["field", 1]]` - 按字段升序
    - `[["field", -1]]` - 按字段降序
    - `[["field1", 1], ["field2", -1]]` - 多字段排序
    """,
    tags=["数据查询"],
    responses={
        200: {
            "description": "查询成功",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "查询单个文档成功",
                        "data": {
                            "name": "张三",
                            "age": 28,
                            "email": "zhangsan@example.com",
                            "department": "技术部"
                        },
                        "timestamp": "2024-01-01T12:00:00"
                    }
                }
            }
        },
        200: {
            "description": "没有找到匹配的文档",
            "content": {
                "application/json": {
                    "example": {
                        "status": "info",
                        "message": "没有找到匹配的文档",
                        "data": None,
                        "timestamp": "2024-01-01T12:00:00"
                    }
                }
            }
        },
        400: {
            "description": "查询失败",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "查询失败: 无法连接到MongoDB服务器",
                        "timestamp": "2024-01-01T12:00:00"
                    }
                }
            }
        }
    }
)
async def query_one_document(
    request: QueryOneRequest
):
    """
    执行单个文档查询，自动处理连接和断开
    """
    cache_key = None
    use_cache = request.cache_ttl != 0

    # 1. 检查缓存 (如果不强制刷新)
    if use_cache and not request.force_refresh:
        cache_key = redis_cache.generate_cache_key("query_one", request.dict())
        cached_result = redis_cache.get(cache_key)
        if cached_result:
            # 如果命中缓存，直接返回结果，不创建MongoDB连接
            cached_result["message"] = f"查询单个文档成功 (来自缓存)"
            # 添加缓存时间信息
            cached_result["cache_ttl"] = request.cache_ttl
            return ApiResponse(**cached_result)

    # 2. 只有缓存未命中时才创建MongoDB连接和查询
    api = MongoDBQueryAPI()
    
    try:
        # 连接数据库
        connection_result = api.connect_to_mongodb(
            request.connection_string,
            request.database_name,
            request.collection_name
        )
        
        if connection_result["status"] == "error":
            return ApiResponse(
                status="error",
                message=f"连接失败: {connection_result['message']}",
                timestamp=datetime.now().isoformat()
            )
        
        # 转换排序格式
        sort_list = None
        if request.sort:
            sort_list = [(item[0], item[1]) for item in request.sort]
        
        # 执行查询
        result = api.query_one_document(
            query_filter=request.query_filter,
            projection=request.projection,
            sort=sort_list
        )
        
        # 3. 设置缓存 (如果查询成功且启用了缓存)
        if use_cache and result["status"] == "success":
            if cache_key is None: # 如果是强制刷新，之前没生成key
                cache_key = redis_cache.generate_cache_key("query_one", request.dict())
            redis_cache.set(cache_key, result, ttl=request.cache_ttl)
            # 添加缓存时间信息到响应
            result["cache_ttl"] = request.cache_ttl

        return ApiResponse(**result)
        
    except Exception as e:
        return ApiResponse(
            status="error",
            message=f"查询过程中发生错误: {str(e)}",
            timestamp=datetime.now().isoformat()
        )
    finally:
        # 确保连接被关闭
        api.close_connection()

@app.post(
    "/aggregate", 
    response_model=ApiResponse,
    summary="执行聚合管道查询（自动连接和断开）",
    description="""
    执行MongoDB聚合管道查询，自动处理连接和断开。
    
    **功能特点：**
    - 自动连接指定的MongoDB数据库
    - 执行聚合查询操作
    - 自动断开连接，释放资源
    - 支持所有MongoDB聚合功能
    
    **常用聚合操作：**
    - `$match`: 过滤文档
    - `$group`: 分组统计
    - `$sort`: 排序
    - `$limit`: 限制数量
    - `$skip`: 跳过数量
    - `$project`: 字段投影
    - `$lookup`: 关联查询
    
    **聚合函数：**
    - `$sum`: 求和
    - `$avg`: 平均值
    - `$max`: 最大值
    - `$min`: 最小值
    - `$count`: 计数
    """,
    tags=["聚合查询"],
    responses={
        200: {
            "description": "聚合查询成功",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "聚合查询成功，返回 2 个文档",
                        "data": [
                            {"_id": "技术部", "count": 5, "avg_age": 30.2, "avg_salary": 18000},
                            {"_id": "销售部", "count": 3, "avg_age": 28.5, "avg_salary": 15000}
                        ],
                        "count": 2,
                        "timestamp": "2024-01-01T12:00:00"
                    }
                }
            }
        }
    }
)
async def aggregate_documents(
    request: AggregateRequest
):
    """
    执行聚合查询，自动处理连接和断开
    """
    cache_key = None
    use_cache = request.cache_ttl != 0

    # 1. 检查缓存 (如果不强制刷新)
    if use_cache and not request.force_refresh:
        cache_key = redis_cache.generate_cache_key("aggregate", request.dict())
        cached_result = redis_cache.get(cache_key)
        if cached_result:
            # 如果命中缓存，直接返回结果，不创建MongoDB连接
            cached_result["message"] = f"聚合查询成功 (来自缓存)，返回 {cached_result.get('count', 0)} 个文档"
            # 添加缓存时间信息
            cached_result["cache_ttl"] = request.cache_ttl
            return ApiResponse(**cached_result)

    # 2. 只有缓存未命中时才创建MongoDB连接和查询
    api = MongoDBQueryAPI()
    
    try:
        # 连接数据库
        connection_result = api.connect_to_mongodb(
            request.connection_string,
            request.database_name,
            request.collection_name
        )
        
        if connection_result["status"] == "error":
            return ApiResponse(
                status="error",
                message=f"连接失败: {connection_result['message']}",
                timestamp=datetime.now().isoformat()
            )
        
        # 执行聚合查询
        result = api.aggregate_pipeline(request.pipeline)
        
        # 3. 设置缓存 (如果查询成功且启用了缓存)
        if use_cache and result["status"] == "success":
            if cache_key is None: # 如果是强制刷新，之前没生成key
                cache_key = redis_cache.generate_cache_key("aggregate", request.dict())
            redis_cache.set(cache_key, result, ttl=request.cache_ttl)
            # 添加缓存时间信息到响应
            result["cache_ttl"] = request.cache_ttl

        return ApiResponse(**result)
        
    except Exception as e:
        return ApiResponse(
            status="error",
            message=f"聚合查询过程中发生错误: {str(e)}",
            timestamp=datetime.now().isoformat()
        )
    finally:
        # 确保连接被关闭
        api.close_connection()

@app.post(
    "/distinct", 
    response_model=ApiResponse,
    summary="查询字段唯一值（自动连接和断开）",
    description="""
    查询指定字段的唯一值，自动处理连接和断开。
    
    **功能特点：**
    - 自动连接指定的MongoDB数据库
    - 执行distinct查询操作
    - 自动断开连接，释放资源
    - 支持可选的查询条件过滤
    
    **使用场景：**
    - 获取所有部门列表
    - 获取所有城市列表
    - 获取所有状态值
    - 获取满足条件的唯一值
    
    **查询条件示例：**
    - 无过滤：查询所有文档的字段唯一值
    - 条件过滤：`{"age": {"$gte": 25}}` - 只查询年龄大于25的文档的字段唯一值
    - 状态过滤：`{"status": "active"}` - 只查询活跃状态的文档的字段唯一值
    """,
    tags=["数据查询"],
    responses={
        200: {
            "description": "distinct查询成功",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "distinct查询成功，字段 'department' 返回 3 个唯一值",
                        "data": {
                            "field": "department",
                            "values": ["技术部", "销售部", "人事部"],
                            "count": 3
                        },
                        "count": 3,
                        "timestamp": "2024-01-01T12:00:00"
                    }
                }
            }
        },
        400: {
            "description": "distinct查询失败",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "distinct查询失败: 无法连接到MongoDB服务器",
                        "timestamp": "2024-01-01T12:00:00"
                    }
                }
            }
        }
    }
)
async def distinct_documents(
    request: DistinctRequest
):
    """
    执行distinct查询，自动处理连接和断开
    """
    cache_key = None
    use_cache = request.cache_ttl != 0

    # 1. 检查缓存 (如果不强制刷新)
    if use_cache and not request.force_refresh:
        cache_key = redis_cache.generate_cache_key("distinct", request.dict())
        cached_result = redis_cache.get(cache_key)
        if cached_result:
            # 如果命中缓存，直接返回结果，不创建MongoDB连接
            cached_result["message"] = f"distinct查询成功 (来自缓存)，字段 '{request.field}' 返回 {cached_result.get('data', {}).get('count', 0)} 个唯一值"
            # 添加缓存时间信息
            cached_result["cache_ttl"] = request.cache_ttl
            return ApiResponse(**cached_result)

    # 2. 只有缓存未命中时才创建MongoDB连接和查询
    api = MongoDBQueryAPI()
    
    try:
        # 连接数据库
        connection_result = api.connect_to_mongodb(
            request.connection_string,
            request.database_name,
            request.collection_name
        )
        
        if connection_result["status"] == "error":
            return ApiResponse(
                status="error",
                message=f"连接失败: {connection_result['message']}",
                timestamp=datetime.now().isoformat()
            )
        
        # 执行distinct查询
        result = api.distinct_values(request.field, request.query_filter)
        
        # 3. 设置缓存 (如果查询成功且启用了缓存)
        if use_cache and result["status"] == "success":
            if cache_key is None: # 如果是强制刷新，之前没生成key
                cache_key = redis_cache.generate_cache_key("distinct", request.dict())
            redis_cache.set(cache_key, result, ttl=request.cache_ttl)
            # 添加缓存时间信息到响应
            result["cache_ttl"] = request.cache_ttl

        return ApiResponse(**result)
        
    except Exception as e:
        return ApiResponse(
            status="error",
            message=f"distinct查询过程中发生错误: {str(e)}",
            timestamp=datetime.now().isoformat()
        )
    finally:
        # 确保连接被关闭
        api.close_connection()

@app.get(
    "/stats", 
    response_model=ApiResponse,
    summary="获取集合统计信息",
    description="""
    获取当前连接集合的详细统计信息。
    
    **返回信息包括：**
    - 集合名称
    - 文档数量
    - 数据大小
    - 平均文档大小
    - 存储大小
    - 索引数量
    """,
    tags=["统计信息"],
    responses={
        200: {
            "description": "获取统计信息成功",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "获取集合统计信息成功",
                        "data": {
                            "collection_name": "test_db.users",
                            "count": 100,
                            "size": 1024000,
                            "avgObjSize": 10240,
                            "storageSize": 2048000,
                            "indexes": 3
                        },
                        "timestamp": "2024-01-01T12:00:00"
                    }
                }
            }
        }
    }
)
async def get_collection_stats(
    api: MongoDBQueryAPI = Depends(get_mongodb_api)
):
    result = api.get_collection_stats()
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return ApiResponse(**result)

@app.post(
    "/disconnect", 
    response_model=ApiResponse,
    summary="断开MongoDB连接",
    description="断开当前MongoDB连接，释放资源。",
    tags=["连接管理"],
    responses={
        200: {
            "description": "断开连接成功",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "MongoDB连接已关闭",
                        "timestamp": "2024-01-01T12:00:00"
                    }
                }
            }
        }
    }
)
async def disconnect_mongodb(
    api: MongoDBQueryAPI = Depends(get_mongodb_api)
):
    result = api.close_connection()
    return ApiResponse(**result)

@app.get(
    "/health", 
    response_model=ApiResponse,
    summary="健康检查",
    description="检查API服务运行状态。",
    tags=["系统状态"],
    responses={
        200: {
            "description": "服务正常",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "message": "MongoDB查询API运行正常",
                        "timestamp": "2024-01-01T12:00:00"
                    }
                }
            }
        }
    }
)
async def health_check():
    return ApiResponse(
        status="healthy",
        message="MongoDB查询API运行正常",
        timestamp=datetime.now().isoformat()
    )

@app.get(
    "/", 
    summary="API信息",
    description="获取API基本信息和使用说明。",
    tags=["系统信息"],
    responses={
        200: {
            "description": "API信息",
            "content": {
                "application/json": {
                    "example": {
                        "message": "MongoDB查询API",
                        "version": "1.0.0",
                        "description": "一个完整的MongoDB查询接口，支持各种查询操作",
                        "endpoints": {
                            "连接管理": {
                                "connect": "POST /connect - 连接MongoDB",
                                "disconnect": "POST /disconnect - 断开连接"
                            },
                            "数据查询": {
                                "query": "POST /query - 查询文档（自动连接断开）",
                                "query_one": "POST /query_one - 查询单个文档（自动连接断开）",
                                "aggregate": "POST /aggregate - 聚合查询（自动连接断开）",
                                "distinct": "POST /distinct - 查询字段唯一值（自动连接断开）"
                            },
                            "统计信息": {
                                "stats": "GET /stats - 获取统计信息"
                            },
                            "系统状态": {
                                "health": "GET /health - 健康检查",
                                "docs": "GET /docs - Swagger API文档",
                                "redoc": "GET /redoc - ReDoc API文档"
                            }
                        },
                        "swagger_ui": "/docs",
                        "redoc": "/redoc",
                        "timestamp": "2024-01-01T12:00:00"
                    }
                }
            }
        }
    }
)
async def root():
    return {
        "message": "MongoDB查询API",
        "version": "1.0.0",
        "description": "一个完整的MongoDB查询接口，支持各种查询操作",
        "endpoints": {
            "连接管理": {
                "connect": "POST /connect - 连接MongoDB",
                "disconnect": "POST /disconnect - 断开连接"
            },
            "数据查询": {
                "query": "POST /query - 查询文档（自动连接断开）",
                "query_one": "POST /query_one - 查询单个文档（自动连接断开）",
                "aggregate": "POST /aggregate - 聚合查询（自动连接断开）",
                "distinct": "POST /distinct - 查询字段唯一值（自动连接断开）"
            },
            "统计信息": {
                "stats": "GET /stats - 获取统计信息"
            },
            "系统状态": {
                "health": "GET /health - 健康检查",
                "docs": "GET /docs - Swagger API文档",
                "redoc": "GET /redoc - ReDoc API文档"
            }
        },
        "swagger_ui": "/docs",
        "redoc": "/redoc",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "fastapi_mongodb:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 