#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新版MongoDB查询API
验证自动连接断开功能
"""

import requests
import json
import time
from datetime import datetime

def test_new_query_api():
    """测试新版查询API"""
    print("🧪 测试新版查询API（自动连接断开）")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 测试数据
    test_cases = [
        {
            "name": "简单查询",
            "data": {
                "connection_string": "mongodb://localhost:27017/",
                "database_name": "test_db",
                "collection_name": "users",
                "query_filter": {"age": {"$gte": 25}},
                "projection": {"name": 1, "age": 1, "email": 1, "_id": 0},
                "limit": 5
            }
        },
        {
            "name": "复杂查询",
            "data": {
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
                "sort": [["salary", -1]],
                "limit": 10
            }
        },
        {
            "name": "聚合查询",
            "data": {
                "connection_string": "mongodb://localhost:27017/",
                "database_name": "test_db",
                "collection_name": "users",
                "pipeline": [
                    {"$match": {"age": {"$gte": 25}}},
                    {"$group": {
                        "_id": "$department",
                        "count": {"$sum": 1},
                        "avg_age": {"$avg": "$age"},
                        "avg_salary": {"$avg": "$salary"}
                    }},
                    {"$sort": {"count": -1}}
                ]
            }
        }
    ]
    
    # 测试查询接口
    print("\n📋 测试查询接口...")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 30)
        
        try:
            start_time = time.time()
            response = requests.post(f"{base_url}/query", json=test_case['data'])
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 成功 - 耗时: {end_time - start_time:.3f}秒")
                print(f"   状态: {result.get('status')}")
                print(f"   消息: {result.get('message')}")
                print(f"   数据条数: {result.get('count', 0)}")
                
                # 显示部分数据
                if result.get('data') and len(result['data']) > 0:
                    print(f"   示例数据: {json.dumps(result['data'][0], ensure_ascii=False)}")
            else:
                print(f"❌ 失败 - HTTP {response.status_code}")
                print(f"   错误: {response.text}")
                
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
    
    # 测试聚合接口
    print("\n📊 测试聚合接口...")
    aggregate_test = {
        "connection_string": "mongodb://localhost:27017/",
        "database_name": "test_db",
        "collection_name": "users",
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
    
    try:
        start_time = time.time()
        response = requests.post(f"{base_url}/aggregate", json=aggregate_test)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 聚合查询成功 - 耗时: {end_time - start_time:.3f}秒")
            print(f"   状态: {result.get('status')}")
            print(f"   消息: {result.get('message')}")
            print(f"   数据条数: {result.get('count', 0)}")
            
            if result.get('data'):
                print("   聚合结果:")
                for item in result['data']:
                    print(f"     {item}")
        else:
            print(f"❌ 聚合查询失败 - HTTP {response.status_code}")
            print(f"   错误: {response.text}")
            
    except Exception as e:
        print(f"❌ 聚合查询异常: {str(e)}")

def test_error_handling():
    """测试错误处理"""
    print("\n🚨 测试错误处理...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 测试无效连接
    print("\n1. 测试无效连接...")
    invalid_connection = {
        "connection_string": "mongodb://invalid-host:27017/",
        "database_name": "test_db",
        "collection_name": "users",
        "query_filter": {"age": {"$gte": 25}},
        "limit": 5
    }
    
    try:
        response = requests.post(f"{base_url}/query", json=invalid_connection)
        result = response.json()
        print(f"   状态: {result.get('status')}")
        print(f"   消息: {result.get('message')}")
    except Exception as e:
        print(f"   异常: {str(e)}")
    
    # 测试无效查询语法
    print("\n2. 测试无效查询语法...")
    invalid_query = {
        "connection_string": "mongodb://localhost:27017/",
        "database_name": "test_db",
        "collection_name": "users",
        "query_filter": {"$invalid_operator": "value"},
        "limit": 5
    }
    
    try:
        response = requests.post(f"{base_url}/query", json=invalid_query)
        result = response.json()
        print(f"   状态: {result.get('status')}")
        print(f"   消息: {result.get('message')}")
    except Exception as e:
        print(f"   异常: {str(e)}")

def test_performance():
    """测试性能"""
    print("\n⚡ 测试性能...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 测试多次查询的性能
    test_data = {
        "connection_string": "mongodb://localhost:27017/",
        "database_name": "test_db",
        "collection_name": "users",
        "query_filter": {"age": {"$gte": 25}},
        "projection": {"name": 1, "age": 1, "_id": 0},
        "limit": 10
    }
    
    print("执行10次查询测试...")
    times = []
    
    for i in range(10):
        try:
            start_time = time.time()
            response = requests.post(f"{base_url}/query", json=test_data)
            end_time = time.time()
            
            if response.status_code == 200:
                times.append(end_time - start_time)
                print(f"   第{i+1}次: {end_time - start_time:.3f}秒")
            else:
                print(f"   第{i+1}次: 失败")
                
        except Exception as e:
            print(f"   第{i+1}次: 异常 - {str(e)}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n📊 性能统计:")
        print(f"   平均耗时: {avg_time:.3f}秒")
        print(f"   最短耗时: {min_time:.3f}秒")
        print(f"   最长耗时: {max_time:.3f}秒")
        print(f"   总耗时: {sum(times):.3f}秒")

def check_api_health():
    """检查API健康状态"""
    print("🏥 检查API健康状态...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # 检查健康状态
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API服务正常")
            print(f"   状态: {result.get('status')}")
            print(f"   消息: {result.get('message')}")
        else:
            print(f"❌ API服务异常 - HTTP {response.status_code}")
        
        # 检查API信息
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API信息获取成功")
            print(f"   版本: {result.get('version')}")
            print(f"   描述: {result.get('description')}")
        else:
            print(f"❌ API信息获取失败 - HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")

def main():
    """主函数"""
    print("🚀 MongoDB查询API测试")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查API健康状态
    check_api_health()
    
    # 测试新版查询API
    test_new_query_api()
    
    # 测试错误处理
    test_error_handling()
    
    # 测试性能
    test_performance()
    
    print(f"\n✅ 测试完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 