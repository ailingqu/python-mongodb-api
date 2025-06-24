#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试query_one查询功能
"""

import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000"

def test_query_one_api():
    """测试query_one API功能"""
    
    print("=== 测试query_one查询功能 ===\n")
    
    # 测试数据
    test_data = {
        "connection_string": "mongodb://localhost:27017/",
        "database_name": "test_db",
        "collection_name": "users",
        "query_filter": {"age": {"$gte": 25}},
        "projection": {"name": 1, "age": 1, "department": 1, "_id": 0},
        "sort": [["age", -1]],
        "cache_ttl": 300
    }
    
    # 1. 测试基本query_one查询
    print("1. 测试基本query_one查询")
    print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/query_one", json=test_data)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. 测试根据ID查询单个文档
    print("2. 测试根据ID查询单个文档")
    test_data_by_id = {
        "connection_string": "mongodb://localhost:27017/",
        "database_name": "test_db",
        "collection_name": "users",
        "query_filter": {"name": "张三"},
        "projection": {"name": 1, "age": 1, "email": 1, "department": 1, "_id": 0}
    }
    print(f"请求数据: {json.dumps(test_data_by_id, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/query_one", json=test_data_by_id)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # 3. 测试查询不存在的文档
    print("3. 测试查询不存在的文档")
    test_data_not_found = {
        "connection_string": "mongodb://localhost:27017/",
        "database_name": "test_db",
        "collection_name": "users",
        "query_filter": {"name": "不存在的用户"},
        "projection": {"name": 1, "age": 1, "_id": 0}
    }
    print(f"请求数据: {json.dumps(test_data_not_found, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/query_one", json=test_data_not_found)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # 4. 测试获取最新文档
    print("4. 测试获取最新文档（按年龄降序）")
    test_data_latest = {
        "connection_string": "mongodb://localhost:27017/",
        "database_name": "test_db",
        "collection_name": "users",
        "projection": {"name": 1, "age": 1, "department": 1, "_id": 0},
        "sort": [["age", -1]]  # 按年龄降序，获取年龄最大的
    }
    print(f"请求数据: {json.dumps(test_data_latest, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/query_one", json=test_data_latest)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # 5. 测试缓存功能
    print("5. 测试缓存功能")
    print("第一次请求（设置缓存）:")
    try:
        response1 = requests.post(f"{BASE_URL}/query_one", json=test_data)
        print(f"响应状态码: {response1.status_code}")
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"响应消息: {result1.get('message', '')}")
    except Exception as e:
        print(f"请求异常: {str(e)}")
    
    print("\n第二次请求（应该从缓存获取）:")
    try:
        response2 = requests.post(f"{BASE_URL}/query_one", json=test_data)
        print(f"响应状态码: {response2.status_code}")
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"响应消息: {result2.get('message', '')}")
    except Exception as e:
        print(f"请求异常: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # 6. 测试强制刷新缓存
    print("6. 测试强制刷新缓存")
    test_data_force_refresh = {
        **test_data,
        "force_refresh": True
    }
    print(f"请求数据: {json.dumps(test_data_force_refresh, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/query_one", json=test_data_force_refresh)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应消息: {result.get('message', '')}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {str(e)}")

def test_error_cases():
    """测试错误情况"""
    
    print("\n=== 测试错误情况 ===\n")
    
    # 1. 测试无效的连接字符串
    print("1. 测试无效的连接字符串")
    test_data_invalid_connection = {
        "connection_string": "mongodb://invalid-host:27017/",
        "database_name": "test_db",
        "collection_name": "users",
        "query_filter": {"age": {"$gte": 25}}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query_one", json=test_data_invalid_connection)
        print(f"响应状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"响应结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. 测试不存在的集合
    print("2. 测试不存在的集合")
    test_data_invalid_collection = {
        "connection_string": "mongodb://localhost:27017/",
        "database_name": "test_db",
        "collection_name": "non_existent_collection",
        "query_filter": {"age": {"$gte": 25}}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query_one", json=test_data_invalid_collection)
        print(f"响应状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"响应结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {str(e)}")

def compare_query_vs_query_one():
    """对比query和query_one的区别"""
    
    print("\n=== 对比query和query_one的区别 ===\n")
    
    # 相同的查询条件
    base_data = {
        "connection_string": "mongodb://localhost:27017/",
        "database_name": "test_db",
        "collection_name": "users",
        "query_filter": {"age": {"$gte": 25}},
        "projection": {"name": 1, "age": 1, "department": 1, "_id": 0},
        "sort": [["age", -1]]
    }
    
    # 测试query接口
    print("1. 使用query接口（返回多个文档）:")
    query_data = {**base_data, "limit": 5}
    try:
        response = requests.post(f"{BASE_URL}/query", json=query_data)
        if response.status_code == 200:
            result = response.json()
            print(f"返回文档数量: {result.get('count', 0)}")
            print(f"数据: {json.dumps(result.get('data', []), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"请求异常: {str(e)}")
    
    print("\n2. 使用query_one接口（返回单个文档）:")
    try:
        response = requests.post(f"{BASE_URL}/query_one", json=base_data)
        if response.status_code == 200:
            result = response.json()
            print(f"返回文档数量: {result.get('count', 0)}")
            print(f"数据: {json.dumps(result.get('data', {}), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"请求异常: {str(e)}")

if __name__ == "__main__":
    print(f"开始测试query_one查询功能 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("请确保MongoDB服务正在运行，并且test_db.users集合中有测试数据")
    print("如果没有测试数据，请先运行example_usage.py创建测试数据\n")
    
    # 测试正常功能
    test_query_one_api()
    
    # 测试错误情况
    test_error_cases()
    
    # 对比功能
    compare_query_vs_query_one()
    
    print(f"\n测试完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 