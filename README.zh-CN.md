[🇺🇸 English README](./README.md)

# MongoDB查询接口

一个完整的Python MongoDB查询接口，支持直接API调用和HTTP RESTful API两种使用方式，内置优化的Swagger UI文档。

## 功能特性

- 🔌 **灵活的连接管理** - 支持自定义MongoDB连接字符串
- 🔍 **强大的查询功能** - 支持简单查询、复杂条件查询、聚合查询
- 🎯 **单个文档查询** - 支持query_one查询，获取单个文档
- 🎯 **唯一值查询** - 支持distinct查询，获取字段唯一值
- 📊 **数据统计** - 获取集合统计信息
- 🌐 **HTTP API** - 提供RESTful API接口
- 📚 **Swagger文档** - 内置优化的Swagger UI，支持在线测试
- 🛡️ **错误处理** - 完善的异常处理和错误信息
- 📝 **日志记录** - 详细的操作日志
- 🔄 **连接池管理** - 自动连接管理和资源释放
- ⚡ **自动连接管理** - 新版API支持自动连接和断开
- 🔄 **强制刷新缓存** - 支持强制从数据库重新获取数据
- 🛡️ **Redis容错** - Redis服务异常时，自动降级服务，不影响核心功能

## 安装依赖

```bash
pip install -r requirements.txt
```

## 项目结构

```
python-mongodb-api/
├── mongodb_api.py          # 核心MongoDB查询API类
├── fastapi_mongodb.py      # FastAPI HTTP接口
├── swagger_config.py       # Swagger UI配置
├── start_api.py           # 启动脚本
├── example_usage.py        # 使用示例
├── config.py              # 配置文件
├── requirements.txt        # 依赖包列表
└── README.md              # 项目说明文档
```

## 快速开始

### 1. 启动API服务

#### 使用启动脚本（推荐）
```bash
# 默认配置启动
python start_api.py

# 开发模式（自动重载）
python start_api.py --reload

# 指定端口
python start_api.py --port 8080

# 调试模式
python start_api.py --log-level debug
```

#### 直接启动
```bash
python fastapi_mongodb.py
```

### 2. 访问Swagger文档

启动服务后，访问以下地址：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

### 3. 使用Swagger UI

1. 打开 http://localhost:8000/docs
2. 查看API文档和示例
3. 使用"Try it out"功能直接测试API
4. 查看请求和响应示例

### 4. API使用方式

#### 新版API（推荐）- 自动连接断开

```python
import requests

# 查询接口 - 自动连接和断开
response = requests.post("http://localhost:8000/query", json={
    "connection_string": "mongodb://localhost:27017/",
    "database_name": "test_db",
    "collection_name": "users",
    "query_filter": {"age": {"$gte": 25}},
    "projection": {"name": 1, "age": 1, "email": 1, "_id": 0},
    "sort": [["age", -1]],
    "limit": 10
})

# 强制刷新缓存
response = requests.post("http://localhost:8000/query", json={
    "connection_string": "mongodb://localhost:27017/",
    "database_name": "test_db",
    "collection_name": "users",
    "query_filter": {"age": {"$gte": 25}},
    "force_refresh": True
})

# 聚合查询 - 自动连接和断开
response = requests.post("http://localhost:8000/aggregate", json={
    "connection_string": "mongodb://localhost:27017/",
    "database_name": "test_db",
    "collection_name": "users",
    "pipeline": [
        {"$match": {"age": {"$gte": 25}}},
        {"$group": {"_id": "$department", "count": {"$sum": 1}}}
    ]
})
```

#### 旧版API - 手动连接断开

```python
import requests

# 1. 连接数据库
response = requests.post("http://localhost:8000/connect", json={
    "connection_string": "mongodb://localhost:27017/",
    "database_name": "test_db",
    "collection_name": "users"
})

# 2. 查询数据
response = requests.post("http://localhost:8000/query", json={
    "query_filter": {"age": {"$gte": 25}},
    "projection": {"name": 1, "age": 1, "email": 1, "_id": 0},
    "sort": [["age", -1]],
    "limit": 5
})

# 3. 断开连接
response = requests.post("http://localhost:8000/disconnect")
```

### 5. 直接使用API类

```python
from mongodb_api import MongoDBQueryAPI

# 创建API实例
api = MongoDBQueryAPI()

# 连接MongoDB
connection_result = api.connect_to_mongodb(
    connection_string="mongodb://localhost:27017/",
    database_name="test_db",
    collection_name="users"
)

# 执行查询
query_result = api.query_documents(
    query_filter={"age": {"$gte": 25}},
    projection={"name": 1, "age": 1, "email": 1, "_id": 0},
    sort=[("age", -1)],
    limit=5
)

# 关闭连接
api.close_connection()
```

## Swagger UI 特性

### 🎨 优化的界面
- 自定义CSS样式，更美观的界面
- 响应式设计，支持移动设备
- 语法高亮，代码更易读

### 🔧 增强功能
- **快速测试按钮** - 一键填充连接参数
- **使用指南** - 内置操作说明
- **请求/响应拦截器** - 自动添加时间戳和日志
- **搜索过滤** - 快速查找API接口
- **深度链接** - 支持直接链接到特定接口

### 📝 详细文档
- 完整的参数说明和示例
- 响应状态码说明
- 错误处理说明
- 使用示例和最佳实践

### 🚀 在线测试
- 支持直接在浏览器中测试API
- 自动生成请求代码
- 实时响应预览
- 请求历史记录

## API端点

### 数据查询（新版 - 推荐）
- `POST /query` - 查询文档（自动连接断开）
- `POST /query_one` - 查询单个文档（自动连接断开）
- `POST /aggregate` - 聚合查询（自动连接断开）
- `POST /distinct` - 查询字段唯一值（自动连接断开）

### 连接管理（旧版）
- `POST /connect` - 连接MongoDB
- `POST /disconnect` - 断开连接

### 统计信息
- `GET /stats` - 获取统计信息

### 系统状态
- `GET /health` - 健康检查
- `GET /` - API信息

## API使用对比

### 新版API（推荐）
**优点：**
- ✅ 一个接口完成所有操作
- ✅ 自动管理连接，无需手动断开
- ✅ 更简洁的使用方式
- ✅ 避免连接泄漏
- ✅ 适合单次查询场景

**使用场景：**
- 单次查询操作
- 快速原型开发
- 简单的数据查询需求

### 旧版API
**优点：**
- ✅ 适合多次查询场景
- ✅ 可以复用连接
- ✅ 更灵活的控制

**缺点：**
- ❌ 需要手动管理连接
- ❌ 容易忘记断开连接
- ❌ 使用步骤较多

**使用场景：**
- 需要多次查询的场景
- 对连接管理有特殊要求
- 需要复用连接的场景

## 详细使用说明

### 连接参数

- `connection_string`: MongoDB连接字符串
  - 本地连接: `mongodb://localhost:27017/`
  - 带认证: `mongodb://username:password@localhost:27017/`
  - 集群连接: `mongodb://host1:port1,host2:port2/`
- `database_name`: 数据库名称
- `collection_name`: 集合名称

### 查询参数

#### query_filter (查询条件)

```python
# 简单条件
{"age": 25}

# 范围查询
{"age": {"$gte": 20, "$lte": 30}}

# 数组查询
{"department": {"$in": ["技术部", "销售部"]}}

# 复杂条件
{
    "$and": [
        {"age": {"$gte": 25}},
        {"status": "active"},
        {"department": {"$ne": "人事部"}}
    ]
}
```

#### projection (投影字段)

```python
# 包含字段
{"name": 1, "age": 1, "email": 1, "_id": 0}

# 排除字段
{"password": 0, "created_at": 0}
```

#### sort (排序)

```python
# 单字段排序
[("age", -1)]  # 降序
[("name", 1)]  # 升序

# 多字段排序
[("department", 1), ("age", -1)]
```

### 聚合查询

```python
pipeline = [
    {"$match": {"age": {"$gte": 25}}},
    {"$group": {
        "_id": "$department",
        "count": {"$sum": 1},
        "avg_age": {"$avg": "$age"},
        "avg_salary": {"$avg": "$salary"}
    }},
    {"$sort": {"count": -1}}
]

result = api.aggregate_pipeline(pipeline)
```

### Query One查询

查询单个文档，只返回第一个匹配的文档。

#### HTTP API使用

```python
import requests

# 基本query_one查询
response = requests.post("http://localhost:8000/query_one", json={
    "connection_string": "mongodb://localhost:27017/",
    "database_name": "test_db",
    "collection_name": "users",
    "query_filter": {"age": {"$gte": 30}},
    "projection": {"name": 1, "age": 1, "department": 1, "_id": 0},
    "sort": [["age", -1]]  # 按年龄降序，获取年龄最大的
})

# 根据ID查询单个文档
response = requests.post("http://localhost:8000/query_one", json={
    "connection_string": "mongodb://localhost:27017/",
    "database_name": "test_db",
    "collection_name": "users",
    "query_filter": {"name": "张三"},
    "projection": {"name": 1, "age": 1, "email": 1, "_id": 0}
})

# 强制刷新缓存
response = requests.post("http://localhost:8000/query_one", json={
    "connection_string": "mongodb://localhost:27017/",
    "database_name": "test_db",
    "collection_name": "users",
    "query_filter": {"department": "技术部"},
    "force_refresh": True
})
```

#### 直接API使用

```python
from mongodb_api import MongoDBQueryAPI

# 创建API实例
api = MongoDBQueryAPI()

# 连接MongoDB
api.connect_to_mongodb(
    connection_string="mongodb://localhost:27017/",
    database_name="test_db",
    collection_name="users"
)

# 查询年龄最大的用户
result = api.query_one_document(
    query_filter={"age": {"$gte": 25}},
    projection={"name": 1, "age": 1, "department": 1, "_id": 0},
    sort=[("age", -1)]
)
print(f"年龄最大的用户: {result['data']}")

# 根据姓名查询用户
result = api.query_one_document(
    query_filter={"name": "张三"},
    projection={"name": 1, "age": 1, "email": 1, "_id": 0}
)
print(f"张三的信息: {result['data']}")

# 关闭连接
api.close_connection()
```

#### 使用场景

- **根据唯一ID查询** - 根据文档ID或其他唯一字段查询单个文档
- **获取第一个匹配文档** - 获取满足条件的第一个文档
- **检查文档是否存在** - 通过查询结果判断文档是否存在
- **获取最新或最旧文档** - 结合排序获取最新或最旧的文档
- **单条记录查询** - 只需要一条记录的场景

#### 响应格式

```json
{
    "status": "success",
    "message": "查询单个文档成功",
    "data": {
        "name": "张三",
        "age": 28,
        "department": "技术部"
    },
    "timestamp": "2024-01-01T12:00:00"
}
```

#### 与query接口的区别

| 特性 | query | query_one |
|------|-------|-----------|
| 返回文档数量 | 多个文档（数组） | 单个文档（对象） |
| 性能 | 需要遍历所有匹配文档 | 只获取第一个文档，性能更好 |
| 使用场景 | 需要多条记录 | 只需要一条记录 |
| 缓存策略 | 缓存整个结果集 | 缓存单个文档 |

### Distinct查询

查询指定字段的唯一值，支持可选的查询条件过滤。

#### HTTP API使用

```python
import requests

# 基本distinct查询（无过滤条件）
response = requests.post("http://localhost:8000/distinct", json={
    "connection_string": "mongodb://localhost:27017/",
    "database_name": "test_db",
    "collection_name": "users",
    "field": "department"
})

# 带过滤条件的distinct查询
response = requests.post("http://localhost:8000/distinct", json={
    "connection_string": "mongodb://localhost:27017/",
    "database_name": "test_db",
    "collection_name": "users",
    "field": "department",
    "query_filter": {"age": {"$gte": 25}},
    "cache_ttl": 300
})

# 强制刷新缓存
response = requests.post("http://localhost:8000/distinct", json={
    "connection_string": "mongodb://localhost:27017/",
    "database_name": "test_db",
    "collection_name": "users",
    "field": "city",
    "force_refresh": True
})
```

#### 直接API使用

```python
from mongodb_api import MongoDBQueryAPI

# 创建API实例
api = MongoDBQueryAPI()

# 连接MongoDB
api.connect_to_mongodb(
    connection_string="mongodb://localhost:27017/",
    database_name="test_db",
    collection_name="users"
)

# 查询所有部门
result = api.distinct_values("department")
print(f"所有部门: {result['data']['values']}")

# 查询年龄大于25岁的用户的部门
result = api.distinct_values("department", {"age": {"$gte": 25}})
print(f"年龄大于25岁的用户部门: {result['data']['values']}")

# 查询所有城市
result = api.distinct_values("city")
print(f"所有城市: {result['data']['values']}")

# 关闭连接
api.close_connection()
```

#### 使用场景

- **获取下拉选项** - 获取部门、城市、状态等下拉列表选项
- **数据去重** - 获取某个字段的所有唯一值
- **条件筛选** - 在满足特定条件的文档中获取字段唯一值
- **数据统计** - 了解数据中某个字段的取值分布

#### 响应格式

```json
{
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
```

## 运行示例

```bash
# 运行使用示例
python example_usage.py

# 启动HTTP API服务
python start_api.py --reload

# 运行核心API示例
python mongodb_api.py
```

## 错误处理

所有方法都返回统一的结果格式：

```python
{
    "status": "success|error|info",
    "message": "操作结果描述",
    "data": {...},  # 成功时返回数据
    "count": 0,     # 数据条数
    "timestamp": "2024-01-01T00:00:00"
}
```

常见错误类型：
- 连接失败
- 查询语法错误
- 权限不足
- 集合不存在

## 性能优化建议

1. **使用索引** - 为常用查询字段创建索引
2. **限制结果集** - 使用 `limit` 参数限制返回数量
3. **投影字段** - 只返回需要的字段
4. **连接池** - 复用数据库连接
5. **批量操作** - 对于大量数据使用批量操作

## 安全注意事项

1. **连接字符串安全** - 不要在代码中硬编码密码
2. **输入验证** - 验证用户输入的查询条件
3. **权限控制** - 使用最小权限原则
4. **SQL注入防护** - 使用参数化查询

## 环境要求

- Python 3.7+
- MongoDB 4.0+
- pymongo 4.0+
- FastAPI 0.100+ (仅HTTP API需要)

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题，请提交Issue或联系开发者。 