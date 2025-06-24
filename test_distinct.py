#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试distinct查询功能
"""

import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000"

def test_distinct_api():
    """测试distinct API功能"""
    
    print("=== 测试distinct查询功能 ===\n")
    
    # 测试数据
    test_data = {
        "connection_string": "mongodb://localhost:27017/",
        "database_name": "test_db",
        "collection_name": "users",
        "field": "department",
        "cache_ttl": 300
    }
    
    # 1. 测试基本distinct查询（无过滤条件）
    print("1. 测试基本distinct查询（无过滤条件）")
    print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/distinct", json=test_data)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. 测试带过滤条件的distinct查询
    print("2. 测试带过滤条件的distinct查询")
    test_data_with_filter = {
        **test_data,
        "query_filter": {"age": {"$gte": 25}}
    }
    print(f"请求数据: {json.dumps(test_data_with_filter, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/distinct", json=test_data_with_filter)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # 3. 测试不同字段的distinct查询
    print("3. 测试不同字段的distinct查询")
    test_data_city = {
        **test_data,
        "field": "city"
    }
    print(f"请求数据: {json.dumps(test_data_city, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/distinct", json=test_data_city)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # 4. 测试缓存功能
    print("4. 测试缓存功能")
    print("第一次请求（设置缓存）:")
    try:
        response1 = requests.post(f"{BASE_URL}/distinct", json=test_data)
        print(f"响应状态码: {response1.status_code}")
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"响应消息: {result1.get('message', '')}")
    except Exception as e:
        print(f"请求异常: {str(e)}")
    
    print("\n第二次请求（应该从缓存获取）:")
    try:
        response2 = requests.post(f"{BASE_URL}/distinct", json=test_data)
        print(f"响应状态码: {response2.status_code}")
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"响应消息: {result2.get('message', '')}")
    except Exception as e:
        print(f"请求异常: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # 5. 测试强制刷新缓存
    print("5. 测试强制刷新缓存")
    test_data_force_refresh = {
        **test_data,
        "force_refresh": True
    }
    print(f"请求数据: {json.dumps(test_data_force_refresh, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/distinct", json=test_data_force_refresh)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应消息: {result.get('message', '')}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # 6. 测试禁用缓存
    print("6. 测试禁用缓存")
    test_data_no_cache = {
        **test_data,
        "cache_ttl": 0
    }
    print(f"请求数据: {json.dumps(test_data_no_cache, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/distinct", json=test_data_no_cache)
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
        "field": "department"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/distinct", json=test_data_invalid_connection)
        print(f"响应状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"响应结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. 测试不存在的字段
    print("2. 测试不存在的字段")
    test_data_invalid_field = {
        "connection_string": "mongodb://localhost:27017/",
        "database_name": "test_db",
        "collection_name": "users",
        "field": "non_existent_field"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/distinct", json=test_data_invalid_field)
        print(f"响应状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"响应结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {str(e)}")

if __name__ == "__main__":
    print(f"开始测试distinct查询功能 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("请确保MongoDB服务正在运行，并且test_db.users集合中有测试数据")
    print("如果没有测试数据，请先运行example_usage.py创建测试数据\n")
    
    # 测试正常功能
    test_distinct_api()
    
    # 测试错误情况
    test_error_cases()
    
    print(f"\n测试完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 