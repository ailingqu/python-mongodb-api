#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB查询接口使用示例
"""

import json
import requests
from mongodb_api import MongoDBQueryAPI

def example_direct_usage():
    """直接使用MongoDB API类的示例"""
    print("=" * 50)
    print("直接使用MongoDB API类示例")
    print("=" * 50)
    
    # 创建API实例
    api = MongoDBQueryAPI()
    
    # MongoDB连接信息（请根据实际情况修改）
    connection_string = "mongodb://localhost:27017/"
    database_name = "test_db"
    collection_name = "users"
    
    # 1. 连接数据库
    print("\n1. 连接MongoDB数据库...")
    connection_result = api.connect_to_mongodb(connection_string, database_name, collection_name)
    print(f"连接结果: {json.dumps(connection_result, ensure_ascii=False, indent=2)}")
    
    if connection_result["status"] != "success":
        print("连接失败，请检查MongoDB服务是否运行")
        return
    
    # 2. 简单查询示例
    print("\n2. 简单查询示例...")
    query_result = api.query_documents(
        query_filter={"age": {"$gte": 25}},
        projection={"name": 1, "age": 1, "email": 1, "_id": 0},
        sort=[("age", -1)],
        limit=5
    )
    print(f"查询结果: {json.dumps(query_result, ensure_ascii=False, indent=2)}")
    
    # 3. 复杂查询示例
    print("\n3. 复杂查询示例...")
    complex_query = {
        "$and": [
            {"age": {"$gte": 20, "$lte": 50}},
            {"department": {"$in": ["技术部", "销售部"]}},
            {"status": "active"}
        ]
    }
    complex_result = api.query_documents(
        query_filter=complex_query,
        projection={"name": 1, "age": 1, "department": 1, "salary": 1, "_id": 0},
        sort=[("salary", -1), ("age", 1)],
        limit=10
    )
    print(f"复杂查询结果: {json.dumps(complex_result, ensure_ascii=False, indent=2)}")
    
    # 4. 聚合查询示例
    print("\n4. 聚合查询示例...")
    pipeline = [
        {"$match": {"age": {"$gte": 25}}},
        {"$group": {
            "_id": "$department",
            "count": {"$sum": 1},
            "avg_age": {"$avg": "$age"},
            "avg_salary": {"$avg": "$salary"},
            "max_salary": {"$max": "$salary"},
            "min_salary": {"$min": "$salary"}
        }},
        {"$sort": {"count": -1}}
    ]
    aggregate_result = api.aggregate_pipeline(pipeline)
    print(f"聚合查询结果: {json.dumps(aggregate_result, ensure_ascii=False, indent=2)}")
    
    # 5. 获取集合统计信息
    print("\n5. 获取集合统计信息...")
    stats_result = api.get_collection_stats()
    print(f"统计信息: {json.dumps(stats_result, ensure_ascii=False, indent=2)}")
    
    # 6. 关闭连接
    print("\n6. 关闭连接...")
    close_result = api.close_connection()
    print(f"关闭结果: {json.dumps(close_result, ensure_ascii=False, indent=2)}")

def example_http_api_usage():
    """使用HTTP API的示例"""
    print("\n" + "=" * 50)
    print("使用HTTP API示例（新版本 - 自动连接断开）")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # 测试API服务是否运行
        response = requests.get(f"{base_url}/health")
        if response.status_code != 200:
            print("❌ API服务未运行，请先启动服务")
            print("运行命令: python start_api.py --reload")
            return
        print("✅ API服务运行正常")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器，请确保FastAPI服务正在运行")
        print("运行命令: python start_api.py --reload")
        return
    
    # 1. 简单查询（自动连接和断开）
    print("\n1. 简单查询（自动连接和断开）...")
    query_data = {
        "connection_string": "mongodb://localhost:27017/",
        "database_name": "test_db",
        "collection_name": "users",
        "query_filter": {"age": {"$gte": 25}},
        "projection": {"name": 1, "age": 1, "email": 1, "_id": 0},
        "sort": [["age", -1]],
        "limit": 5
    }
    
    try:
        response = requests.post(f"{base_url}/query", json=query_data)
        query_result = response.json()
        print(f"查询结果: {json.dumps(query_result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
    
    # 2. 复杂查询示例
    print("\n2. 复杂查询示例...")
    complex_query_data = {
        "connection_string": "mongodb://localhost:27017/",
        "database_name": "test_db",
        "collection_name": "users",
        "query_filter": {
            "$and": [
                {"age": {"$gte": 20, "$lte": 50}},
                {"department": {"$in": ["技术部", "销售部"]}},
                {"status": "active"}
            ]
        },
        "projection": {"name": 1, "age": 1, "department": 1, "salary": 1, "_id": 0},
        "sort": [["salary", -1], ["age", 1]],
        "limit": 10
    }
    
    try:
        response = requests.post(f"{base_url}/query", json=complex_query_data)
        complex_result = response.json()
        print(f"复杂查询结果: {json.dumps(complex_result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 复杂查询失败: {str(e)}")
    
    # 3. 聚合查询
    print("\n3. 聚合查询...")
    aggregate_data = {
        "connection_string": "mongodb://localhost:27017/",
        "database_name": "test_db",
        "collection_name": "users",
        "pipeline": [
            {"$match": {"age": {"$gte": 25}}},
            {"$group": {"_id": "$department", "count": {"$sum": 1}, "avg_age": {"$avg": "$age"}}},
            {"$sort": {"count": -1}}
        ]
    }
    response = requests.post(f"{base_url}/aggregate", json=aggregate_data)
    aggregate_result = response.json()
    print(f"聚合查询结果: {json.dumps(aggregate_result, ensure_ascii=False, indent=2)}")
    
    # 4. 查询单个文档
    print("\n4. 查询单个文档...")
    query_one_data = {
        "connection_string": "mongodb://localhost:27017/",
        "database_name": "test_db",
        "collection_name": "users",
        "query_filter": {"age": {"$gte": 30}},
        "projection": {"name": 1, "age": 1, "department": 1, "_id": 0},
        "sort": [["age", -1]]  # 按年龄降序，获取年龄最大的
    }
    response = requests.post(f"{base_url}/query_one", json=query_one_data)
    query_one_result = response.json()
    print(f"查询单个文档结果: {json.dumps(query_one_result, ensure_ascii=False, indent=2)}")
    
    # 5. 获取API信息
    print("\n5. 获取API信息...")
    try:
        response = requests.get(f"{base_url}/")
        api_info = response.json()
        print(f"API信息: {json.dumps(api_info, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 获取API信息失败: {str(e)}")

def example_legacy_http_api_usage():
    """使用旧版HTTP API的示例（需要手动连接和断开）"""
    print("\n" + "=" * 50)
    print("使用旧版HTTP API示例（手动连接断开）")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 1. 连接数据库
    print("\n1. 连接MongoDB数据库...")
    connection_data = {
        "connection_string": "mongodb://localhost:27017/",
        "database_name": "test_db",
        "collection_name": "users"
    }
    
    try:
        response = requests.post(f"{base_url}/connect", json=connection_data)
        connection_result = response.json()
        print(f"连接结果: {json.dumps(connection_result, ensure_ascii=False, indent=2)}")
        
        if connection_result.get("status") != "success":
            print("连接失败，请检查MongoDB服务是否运行")
            return
    except requests.exceptions.ConnectionError:
        print("无法连接到API服务器，请确保FastAPI服务正在运行")
        print("运行命令: python fastapi_mongodb.py")
        return
    
    # 2. 简单查询
    print("\n2. 简单查询...")
    query_data = {
        "query_filter": {"age": {"$gte": 25}},
        "projection": {"name": 1, "age": 1, "email": 1, "_id": 0},
        "sort": [["age", -1]],
        "limit": 5
    }
    
    response = requests.post(f"{base_url}/query", json=query_data)
    query_result = response.json()
    print(f"查询结果: {json.dumps(query_result, ensure_ascii=False, indent=2)}")
    
    # 3. 聚合查询
    print("\n3. 聚合查询...")
    aggregate_data = {
        "pipeline": [
            {"$match": {"age": {"$gte": 25}}},
            {"$group": {
                "_id": "$department",
                "count": {"$sum": 1},
                "avg_age": {"$avg": "$age"}
            }},
            {"$sort": {"count": -1}}
        ]
    }
    
    response = requests.post(f"{base_url}/aggregate", json=aggregate_data)
    aggregate_result = response.json()
    print(f"聚合查询结果: {json.dumps(aggregate_result, ensure_ascii=False, indent=2)}")
    
    # 4. 获取统计信息
    print("\n4. 获取统计信息...")
    response = requests.get(f"{base_url}/stats")
    stats_result = response.json()
    print(f"统计信息: {json.dumps(stats_result, ensure_ascii=False, indent=2)}")
    
    # 5. 断开连接
    print("\n5. 断开连接...")
    response = requests.post(f"{base_url}/disconnect")
    disconnect_result = response.json()
    print(f"断开连接结果: {json.dumps(disconnect_result, ensure_ascii=False, indent=2)}")

def create_sample_data():
    """创建示例数据的函数"""
    print("\n" + "=" * 50)
    print("创建示例数据")
    print("=" * 50)
    
    api = MongoDBQueryAPI()
    
    # 连接数据库
    connection_result = api.connect_to_mongodb(
        "mongodb://localhost:27017/",
        "test_db",
        "users"
    )
    
    if connection_result["status"] != "success":
        print("连接失败，无法创建示例数据")
        return
    
    # 示例数据
    sample_users = [
        {
            "name": "张三",
            "age": 28,
            "email": "zhangsan@example.com",
            "department": "技术部",
            "position": "软件工程师",
            "salary": 15000,
            "status": "active",
            "join_date": "2022-01-15"
        },
        {
            "name": "李四",
            "age": 32,
            "email": "lisi@example.com",
            "department": "技术部",
            "position": "高级工程师",
            "salary": 20000,
            "status": "active",
            "join_date": "2021-06-20"
        },
        {
            "name": "王五",
            "age": 25,
            "email": "wangwu@example.com",
            "department": "销售部",
            "position": "销售代表",
            "salary": 12000,
            "status": "active",
            "join_date": "2023-03-10"
        },
        {
            "name": "赵六",
            "age": 35,
            "email": "zhaoliu@example.com",
            "department": "销售部",
            "position": "销售经理",
            "salary": 25000,
            "status": "active",
            "join_date": "2020-09-01"
        },
        {
            "name": "钱七",
            "age": 29,
            "email": "qianqi@example.com",
            "department": "人事部",
            "position": "HR专员",
            "salary": 10000,
            "status": "inactive",
            "join_date": "2022-11-05"
        }
    ]
    
    try:
        # 插入示例数据
        api.collection.insert_many(sample_users)
        print(f"成功插入 {len(sample_users)} 条示例数据")
        
        # 验证数据
        count = api.collection.count_documents({})
        print(f"集合中共有 {count} 条数据")
        
    except Exception as e:
        print(f"插入数据时发生错误: {str(e)}")
    finally:
        api.close_connection()

def show_api_comparison():
    """显示新旧API的对比"""
    print("\n" + "=" * 60)
    print("新旧API使用方式对比")
    print("=" * 60)
    
    print("\n📋 新版API（推荐）- 自动连接断开")
    print("-" * 40)
    print("优点：")
    print("✅ 一个接口完成所有操作")
    print("✅ 自动管理连接，无需手动断开")
    print("✅ 更简洁的使用方式")
    print("✅ 避免连接泄漏")
    print("✅ 适合单次查询场景")
    
    print("\n使用示例：")
    print("""
# 查询接口
POST /query
{
    "connection_string": "mongodb://localhost:27017/",
    "database_name": "test_db",
    "collection_name": "users",
    "query_filter": {"age": {"$gte": 25}},
    "limit": 10
}

# 聚合接口
POST /aggregate
{
    "connection_string": "mongodb://localhost:27017/",
    "database_name": "test_db",
    "collection_name": "users",
    "pipeline": [...]
}
    """)
    
    print("\n📋 旧版API - 手动连接断开")
    print("-" * 40)
    print("优点：")
    print("✅ 适合多次查询场景")
    print("✅ 可以复用连接")
    print("✅ 更灵活的控制")
    
    print("缺点：")
    print("❌ 需要手动管理连接")
    print("❌ 容易忘记断开连接")
    print("❌ 使用步骤较多")
    
    print("\n使用示例：")
    print("""
# 1. 连接
POST /connect
{
    "connection_string": "mongodb://localhost:27017/",
    "database_name": "test_db",
    "collection_name": "users"
}

# 2. 查询
POST /query
{
    "query_filter": {"age": {"$gte": 25}},
    "limit": 10
}

# 3. 断开
POST /disconnect
    """)

if __name__ == "__main__":
    print("MongoDB查询接口使用示例")
    print("请确保MongoDB服务正在运行")
    
    # 选择运行模式
    print("\n请选择运行模式:")
    print("1. 直接使用API类")
    print("2. 使用新版HTTP API（自动连接断开）")
    print("3. 使用旧版HTTP API（手动连接断开）")
    print("4. 创建示例数据")
    print("5. 查看API对比")
    
    choice = input("\n请输入选择 (1/2/3/4/5): ").strip()
    
    if choice == "1":
        example_direct_usage()
    elif choice == "2":
        example_http_api_usage()
    elif choice == "3":
        example_legacy_http_api_usage()
    elif choice == "4":
        create_sample_data()
    elif choice == "5":
        show_api_comparison()
    else:
        print("无效选择，运行默认示例...")
        example_http_api_usage() 