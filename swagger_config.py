#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swagger配置文件
用于定制FastAPI的Swagger UI显示效果
"""

# Swagger UI 配置参数
SWAGGER_UI_PARAMETERS = {
    # 基本显示配置
    "defaultModelsExpandDepth": -1,  # 隐藏模型示例
    "docExpansion": "list",  # 展开所有接口 (none, list, full)
    "filter": True,  # 启用搜索过滤
    "showExtensions": True,  # 显示扩展信息
    "showCommonExtensions": True,  # 显示通用扩展
    "tryItOutEnabled": True,  # 启用"Try it out"功能
    "requestSnippetsEnabled": True,  # 启用请求代码片段
    
    # 自定义CSS样式
    "customCss": """
        .swagger-ui .topbar { display: none }
        .swagger-ui .info .title { color: #3b4151; font-size: 36px; }
        .swagger-ui .info .description { font-size: 16px; line-height: 1.6; }
        .swagger-ui .opblock.opblock-get .opblock-summary-method { background: #61affe; }
        .swagger-ui .opblock.opblock-post .opblock-summary-method { background: #49cc90; }
        .swagger-ui .opblock.opblock-put .opblock-summary-method { background: #fca130; }
        .swagger-ui .opblock.opblock-delete .opblock-summary-method { background: #f93e3e; }
        .swagger-ui .opblock-tag { border-bottom: 1px solid #e3e3e3; margin-bottom: 20px; }
        .swagger-ui .opblock-tag-section h3 { color: #3b4151; font-size: 24px; }
        .swagger-ui .opblock-summary-description { color: #666; }
        .swagger-ui .parameter__name { font-weight: bold; }
        .swagger-ui .parameter__type { color: #999; }
        .swagger-ui .parameter__required { color: #f93e3e; }
        .swagger-ui .response-col_status { font-weight: bold; }
        .swagger-ui .response-col_description { color: #666; }
        .swagger-ui .btn.execute { background-color: #4990e2; }
        .swagger-ui .btn.execute:hover { background-color: #357abd; }
        .swagger-ui .scheme-container { background: #f7f7f7; padding: 20px; border-radius: 4px; }
        .swagger-ui .info .base-url { font-size: 14px; color: #666; }
        .swagger-ui .info .title small { color: #999; }
        .swagger-ui .info .title small pre { background: #f7f7f7; padding: 10px; border-radius: 4px; }
    """,
    
    # 自定义JavaScript
    "customJs": """
        // 添加自定义功能
        window.addEventListener('load', function() {
            // 添加API使用说明
            const infoSection = document.querySelector('.info');
            if (infoSection) {
                const usageGuide = document.createElement('div');
                usageGuide.innerHTML = `
                    <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 4px; border-left: 4px solid #007bff;">
                        <h4 style="margin: 0 0 10px 0; color: #007bff;">📖 使用指南</h4>
                        <ol style="margin: 0; padding-left: 20px;">
                            <li>首先调用 <code>/connect</code> 接口连接MongoDB</li>
                            <li>使用 <code>/query</code> 或 <code>/aggregate</code> 进行数据查询</li>
                            <li>可选调用 <code>/stats</code> 获取统计信息</li>
                            <li>最后调用 <code>/disconnect</code> 断开连接</li>
                        </ol>
                    </div>
                `;
                infoSection.appendChild(usageGuide);
            }
            
            // 添加快速测试按钮
            const connectBtn = document.createElement('button');
            connectBtn.textContent = '🔗 快速连接测试';
            connectBtn.style.cssText = 'margin: 10px 0; padding: 8px 16px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer;';
            connectBtn.onclick = function() {
                // 自动填充连接参数
                const connectEndpoint = document.querySelector('[data-path="/connect"]');
                if (connectEndpoint) {
                    connectEndpoint.click();
                    setTimeout(() => {
                        const jsonInput = document.querySelector('.body-param__text');
                        if (jsonInput) {
                            jsonInput.value = JSON.stringify({
                                "connection_string": "mongodb://localhost:27017/",
                                "database_name": "test_db",
                                "collection_name": "users"
                            }, null, 2);
                        }
                    }, 500);
                }
            };
            
            if (infoSection) {
                infoSection.appendChild(connectBtn);
            }
            
            // 美化响应示例
            const style = document.createElement('style');
            style.textContent = `
                .swagger-ui .responses-table .response-col_status {
                    font-weight: bold;
                    text-transform: uppercase;
                }
                .swagger-ui .responses-table .response-col_status.response-200 {
                    color: #28a745;
                }
                .swagger-ui .responses-table .response-col_status.response-400 {
                    color: #dc3545;
                }
                .swagger-ui .responses-table .response-col_status.response-500 {
                    color: #dc3545;
                }
                .swagger-ui .model-example {
                    background: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 4px;
                    padding: 10px;
                    margin: 5px 0;
                }
                .swagger-ui .model-example pre {
                    margin: 0;
                    font-size: 12px;
                }
            `;
            document.head.appendChild(style);
        });
    """,
    
    # 请求拦截器
    # "requestInterceptor": """
    #     function(request) {
    #         console.log('🚀 发送请求:', request);
            
    #         // 添加请求时间戳
    #         if (request.body) {
    #             try {
    #                 const body = JSON.parse(request.body);
    #                 body.timestamp = new Date().toISOString();
    #                 request.body = JSON.stringify(body);
    #             } catch (e) {
    #                 console.warn('无法解析请求体:', e);
    #             }
    #         }
            
    #         return request;
    #     }
    # """,
    
    # 响应拦截器
    # "responseInterceptor": """
    #     function(response) {
    #         console.log('📥 收到响应:', response);
            
    #         // 美化响应显示
    #         if (response.body) {
    #             try {
    #                 const body = JSON.parse(response.body);
    #                 if (body.status === 'success') {
    #                     console.log('✅ 操作成功:', body.message);
    #                 } else if (body.status === 'error') {
    #                     console.error('❌ 操作失败:', body.message);
    #                 }
    #             } catch (e) {
    #                 console.warn('无法解析响应体:', e);
    #             }
    #         }
            
    #         return response;
    #     }
    # """,
    
    # 其他配置
    "displayOperationId": False,  # 不显示操作ID
    "displayRequestDuration": True,  # 显示请求持续时间
    "deepLinking": True,  # 启用深度链接
    "persistAuthorization": True,  # 保持授权状态
    "syntaxHighlight": {
        "activated": True,
        "theme": "monokai"
    }
}

# API标签配置
API_TAGS = [
    {
        "name": "连接管理",
        "description": "MongoDB连接相关操作，包括连接和断开连接",
        "externalDocs": {
            "description": "MongoDB连接文档",
            "url": "https://docs.mongodb.com/manual/reference/connection-string/"
        }
    },
    {
        "name": "数据查询",
        "description": "文档查询操作，支持简单查询和复杂条件查询",
        "externalDocs": {
            "description": "MongoDB查询文档",
            "url": "https://docs.mongodb.com/manual/tutorial/query-documents/"
        }
    },
    {
        "name": "聚合查询",
        "description": "聚合管道查询，支持复杂的数据聚合操作",
        "externalDocs": {
            "description": "MongoDB聚合文档",
            "url": "https://docs.mongodb.com/manual/aggregation/"
        }
    },
    {
        "name": "统计信息",
        "description": "获取集合和数据库的统计信息",
        "externalDocs": {
            "description": "MongoDB统计文档",
            "url": "https://docs.mongodb.com/manual/reference/command/collStats/"
        }
    },
    {
        "name": "系统状态",
        "description": "API服务状态检查和监控",
        "externalDocs": {
            "description": "健康检查文档",
            "url": "https://en.wikipedia.org/wiki/Health_check"
        }
    },
    {
        "name": "系统信息",
        "description": "API基本信息和配置说明",
        "externalDocs": {
            "description": "API文档",
            "url": "https://swagger.io/docs/"
        }
    }
]

# 服务器配置
SERVERS = [
    {
        "url": "http://localhost:8000",
        "description": "本地开发服务器"
    }, 
    {
        "url": "https://api.mexxxxai.win",
        "description": "生产环境域名访问"
    }
]

# 安全配置
SECURITY_SCHEMES = {
    "ApiKeyAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
        "description": "API密钥认证"
    },
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT令牌认证"
    }
}

# 响应示例
RESPONSE_EXAMPLES = {
    "success_response": {
        "summary": "成功响应",
        "description": "操作成功时的响应格式",
        "value": {
            "status": "success",
            "message": "操作成功",
            "data": [],
            "count": 0,
            "timestamp": "2024-01-01T12:00:00"
        }
    },
    "error_response": {
        "summary": "错误响应",
        "description": "操作失败时的响应格式",
        "value": {
            "status": "error",
            "message": "操作失败的具体原因",
            "timestamp": "2024-01-01T12:00:00"
        }
    }
}

# 查询参数示例
QUERY_EXAMPLES = {
    "simple_query": {
        "summary": "简单查询",
        "description": "查询年龄大于25岁的用户",
        "value": {
            "query_filter": {"age": {"$gte": 25}},
            "projection": {"name": 1, "age": 1, "email": 1, "_id": 0},
            "limit": 10
        }
    },
    "complex_query": {
        "summary": "复杂查询",
        "description": "多条件组合查询",
        "value": {
            "query_filter": {
                "$and": [
                    {"age": {"$gte": 20, "$lte": 50}},
                    {"department": {"$in": ["技术部", "销售部"]}},
                    {"status": "active"}
                ]
            },
            "projection": {"name": 1, "age": 1, "department": 1, "salary": 1, "_id": 0},
            "sort": [["salary", -1], ["age", 1]],
            "limit": 20
        }
    },
    "aggregate_example": {
        "summary": "聚合查询",
        "description": "按部门统计用户信息",
        "value": {
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
}

def get_swagger_config():
    """获取完整的Swagger配置"""
    return {
        "swagger_ui_parameters": SWAGGER_UI_PARAMETERS,
        "tags": API_TAGS,
        "servers": SERVERS,
        "security_schemes": SECURITY_SCHEMES,
        "response_examples": RESPONSE_EXAMPLES,
        "query_examples": QUERY_EXAMPLES
    }

if __name__ == "__main__":
    # 测试配置
    config = get_swagger_config()
    print("Swagger配置加载成功!")
    print(f"标签数量: {len(config['tags'])}")
    print(f"服务器数量: {len(config['servers'])}")
    print(f"安全方案数量: {len(config['security_schemes'])}") 