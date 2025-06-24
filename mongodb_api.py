from typing import Dict, List, Any, Optional, Union
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure
import json
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBQueryAPI:
    """MongoDB查询API类"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
    
    def connect_to_mongodb(self, connection_string: str, database_name: str, collection_name: str) -> Dict[str, Any]:
        """
        连接到MongoDB数据库
        
        Args:
            connection_string: MongoDB连接字符串
            database_name: 数据库名称
            collection_name: 集合名称
            
        Returns:
            Dict: 包含连接状态和信息的字典
        """
        try:
            # 创建MongoDB客户端
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            
            # 测试连接
            self.client.admin.command('ping')
            
            # 获取数据库和集合
            self.db = self.client[database_name]
            self.collection = self.db[collection_name]
            
            logger.info(f"成功连接到MongoDB数据库: {database_name}, 集合: {collection_name}")
            
            return {
                "status": "success",
                "message": "连接成功",
                "database": database_name,
                "collection": collection_name,
                "timestamp": datetime.now().isoformat()
            }
            
        except ConnectionFailure as e:
            error_msg = f"连接失败: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        except ServerSelectionTimeoutError as e:
            error_msg = f"服务器选择超时: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def query_documents(self, 
                       query_filter: Dict[str, Any] = None,
                       projection: Dict[str, Any] = None,
                       sort: List[tuple] = None,
                       limit: int = None,
                       skip: int = None) -> Dict[str, Any]:
        """
        查询MongoDB文档
        
        Args:
            query_filter: 查询条件字典
            projection: 投影字段字典
            sort: 排序条件列表，如 [("field", 1)] 或 [("field", -1)]
            limit: 限制返回文档数量
            skip: 跳过文档数量
            
        Returns:
            Dict: 包含查询结果的字典
        """
        if self.collection is None:
            return {
                "status": "error",
                "message": "未连接到MongoDB，请先调用connect_to_mongodb方法",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # 设置默认查询条件
            if query_filter is None:
                query_filter = {}
            
            # 如果projection为空字典，则表示返回所有字段
            if projection == {}:
                projection = None

            # 构建查询
            cursor = self.collection.find(query_filter, projection)
            
            # 应用排序
            if sort:
                cursor = cursor.sort(sort)
            
            # 应用跳过
            if skip is not None:
                cursor = cursor.skip(skip)
            
            # 应用限制
            if limit is not None:
                cursor = cursor.limit(limit)
            
            # 获取结果
            documents = list(cursor)
            
            # 处理ObjectId序列化
            for doc in documents:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            logger.info(f"查询成功，返回 {len(documents)} 个文档")
            
            return {
                "status": "success",
                "message": f"查询成功，返回 {len(documents)} 个文档",
                "data": documents,
                "count": len(documents),
                "query_filter": query_filter,
                "timestamp": datetime.now().isoformat()
            }
            
        except OperationFailure as e:
            error_msg = f"查询操作失败: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            error_msg = f"查询时发生未知错误: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def query_one_document(self, 
                          query_filter: Dict[str, Any] = None,
                          projection: Dict[str, Any] = None,
                          sort: List[tuple] = None) -> Dict[str, Any]:
        """
        查询MongoDB单个文档
        
        Args:
            query_filter: 查询条件字典
            projection: 投影字段字典
            sort: 排序条件列表，如 [("field", 1)] 或 [("field", -1)]
            
        Returns:
            Dict: 包含查询结果的字典
        """
        if self.collection is None:
            return {
                "status": "error",
                "message": "未连接到MongoDB，请先调用connect_to_mongodb方法",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # 设置默认查询条件
            if query_filter is None:
                query_filter = {}
            
            # 如果projection为空字典，则表示返回所有字段
            if projection == {}:
                projection = None

            # 构建查询
            cursor = self.collection.find(query_filter, projection)
            
            # 应用排序
            if sort:
                cursor = cursor.sort(sort)
            
            # 获取第一个文档
            document = cursor.limit(1).next()
            
            # 处理ObjectId序列化
            if '_id' in document:
                document['_id'] = str(document['_id'])
            
            logger.info(f"查询单个文档成功")
            
            return {
                "status": "success",
                "message": "查询单个文档成功",
                "data": document,
                "query_filter": query_filter,
                "timestamp": datetime.now().isoformat()
            }
            
        except StopIteration:
            # 没有找到匹配的文档
            logger.info(f"没有找到匹配的文档")
            return {
                "status": "info",
                "message": "没有找到匹配的文档",
                "data": None,
                "query_filter": query_filter,
                "timestamp": datetime.now().isoformat()
            }
        except OperationFailure as e:
            error_msg = f"查询操作失败: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            error_msg = f"查询时发生未知错误: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def aggregate_pipeline(self, pipeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行聚合管道查询
        
        Args:
            pipeline: 聚合管道列表
            
        Returns:
            Dict: 包含聚合结果的字典
        """
        if self.collection is None:
            return {
                "status": "error",
                "message": "未连接到MongoDB，请先调用connect_to_mongodb方法",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # 执行聚合查询
            cursor = self.collection.aggregate(pipeline)
            documents = list(cursor)
            
            # 处理ObjectId序列化
            for doc in documents:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            logger.info(f"聚合查询成功，返回 {len(documents)} 个文档")
            
            return {
                "status": "success",
                "message": f"聚合查询成功，返回 {len(documents)} 个文档",
                "data": documents,
                "count": len(documents),
                "pipeline": pipeline,
                "timestamp": datetime.now().isoformat()
            }
            
        except OperationFailure as e:
            error_msg = f"聚合查询失败: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            error_msg = f"聚合查询时发生未知错误: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def distinct_values(self, field: str, query_filter: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        查询指定字段的唯一值
        
        Args:
            field: 要查询唯一值的字段名
            query_filter: 可选的查询条件字典，用于过滤文档
            
        Returns:
            Dict: 包含唯一值列表的字典
        """
        if self.collection is None:
            return {
                "status": "error",
                "message": "未连接到MongoDB，请先调用connect_to_mongodb方法",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # 设置默认查询条件
            if query_filter is None:
                query_filter = {}
            
            # 执行distinct查询
            distinct_values = self.collection.distinct(field, query_filter)
            
            # 处理ObjectId序列化
            processed_values = []
            for value in distinct_values:
                if hasattr(value, '__str__') and str(type(value)).find('ObjectId') != -1:
                    processed_values.append(str(value))
                else:
                    processed_values.append(value)
            
            logger.info(f"distinct查询成功，字段 '{field}' 返回 {len(processed_values)} 个唯一值")
            
            return {
                "status": "success",
                "message": f"distinct查询成功，字段 '{field}' 返回 {len(processed_values)} 个唯一值",
                "data": {
                    "field": field,
                    "values": processed_values,
                    "count": len(processed_values)
                },
                "query_filter": query_filter,
                "timestamp": datetime.now().isoformat()
            }
            
        except OperationFailure as e:
            error_msg = f"distinct查询失败: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            error_msg = f"distinct查询时发生未知错误: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        获取集合统计信息
        
        Returns:
            Dict: 包含集合统计信息的字典
        """
        if self.collection is None:
            return {
                "status": "error",
                "message": "未连接到MongoDB，请先调用connect_to_mongodb方法",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # 获取集合统计信息
            stats = self.db.command("collstats", self.collection.name)
            
            return {
                "status": "success",
                "message": "获取集合统计信息成功",
                "data": {
                    "collection_name": stats.get("ns", ""),
                    "count": stats.get("count", 0),
                    "size": stats.get("size", 0),
                    "avgObjSize": stats.get("avgObjSize", 0),
                    "storageSize": stats.get("storageSize", 0),
                    "indexes": stats.get("nindexes", 0)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"获取集合统计信息失败: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def close_connection(self) -> Dict[str, Any]:
        """
        关闭MongoDB连接
        
        Returns:
            Dict: 包含关闭状态信息的字典
        """
        try:
            if self.client:
                self.client.close()
                self.client = None
                self.db = None
                self.collection = None
                
                logger.info("MongoDB连接已关闭")
                
                return {
                    "status": "success",
                    "message": "MongoDB连接已关闭",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "info",
                    "message": "没有活动的MongoDB连接",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            error_msg = f"关闭连接时发生错误: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def __del__(self):
        """析构函数，确保连接被关闭"""
        self.close_connection()


# 使用示例函数
def example_usage():
    """使用示例"""
    
    # 创建API实例
    api = MongoDBQueryAPI()
    
    # MongoDB连接信息
    connection_string = "mongodb://localhost:27017/"
    database_name = "test_db"
    collection_name = "users"
    
    # 连接数据库
    print("=== 连接MongoDB ===")
    connection_result = api.connect_to_mongodb(connection_string, database_name, collection_name)
    print(json.dumps(connection_result, ensure_ascii=False, indent=2))
    
    if connection_result["status"] == "success":
        # 简单查询示例
        print("\n=== 简单查询示例 ===")
        query_result = api.query_documents(
            query_filter={"age": {"$gte": 25}},
            projection={"name": 1, "age": 1, "email": 1, "_id": 0},
            sort=[("age", -1)],
            limit=5
        )
        print(json.dumps(query_result, ensure_ascii=False, indent=2))
        
        # 查询单个文档示例
        print("\n=== 查询单个文档示例 ===")
        query_one_result = api.query_one_document(
            query_filter={"age": {"$gte": 25}},
            projection={"name": 1, "age": 1, "email": 1, "_id": 0},
            sort=[("age", -1)]  # 按年龄降序，获取年龄最大的
        )
        print(json.dumps(query_one_result, ensure_ascii=False, indent=2))
        
        # 聚合查询示例
        print("\n=== 聚合查询示例 ===")
        pipeline = [
            {"$group": {"_id": "$department", "count": {"$sum": 1}, "avg_age": {"$avg": "$age"}}},
            {"$sort": {"count": -1}}
        ]
        aggregate_result = api.aggregate_pipeline(pipeline)
        print(json.dumps(aggregate_result, ensure_ascii=False, indent=2))
        
        # distinct查询示例
        print("\n=== distinct查询示例 ===")
        # 查询所有部门
        distinct_dept_result = api.distinct_values("department")
        print("所有部门:")
        print(json.dumps(distinct_dept_result, ensure_ascii=False, indent=2))
        
        # 查询年龄大于25岁的用户的部门
        distinct_dept_filtered_result = api.distinct_values("department", {"age": {"$gte": 25}})
        print("年龄大于25岁的用户部门:")
        print(json.dumps(distinct_dept_filtered_result, ensure_ascii=False, indent=2))
        
        # 查询所有城市
        distinct_city_result = api.distinct_values("city")
        print("所有城市:")
        print(json.dumps(distinct_city_result, ensure_ascii=False, indent=2))
        
        # 获取集合统计信息
        print("\n=== 集合统计信息 ===")
        stats_result = api.get_collection_stats()
        print(json.dumps(stats_result, ensure_ascii=False, indent=2))
        
        # 关闭连接
        print("\n=== 关闭连接 ===")
        close_result = api.close_connection()
        print(json.dumps(close_result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    example_usage() 