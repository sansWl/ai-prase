from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os
from dotenv import load_dotenv

load_dotenv()


def setup_cors(app: FastAPI):
    """
    配置跨域资源共享 (CORS)
    
    Args:
        app: FastAPI 应用实例
    """
    # 从环境变量读取允许的来源，如果没有则使用默认值
    allowed_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:8080"
    )
    
    # 将逗号分隔的字符串转换为列表
    origins = [origin.strip() for origin in allowed_origins.split(",")]
    
    # 添加 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # 允许访问的源
        allow_credentials=True,  # 支持 cookie
        allow_methods=["*"],  # 允许使用的 HTTP 方法
        allow_headers=["*"],  # 允许使用的请求头
    )
    
    return app
