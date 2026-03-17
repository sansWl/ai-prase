from threading import Thread
from fastapi import FastAPI, File, UploadFile, APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from factories.threadFactory.redis_channel import asynio_instance
from utils import redisUtils, logger,neo4jUtils,crypto_utils,env_config
from utils.rag_system import get_rag_system
from factories.llmsFactory.llms_factory import LLMsFactory
from factories.embeddingFactory.embedding_factory import EmbeddingFactory
from web_server.global_handler.exception_handler import register_exception_handlers
from web_server.global_handler.cors_config import setup_cors
from utils.embedding_tool import  get_instance
from utils.llm_prompt.llm_utils import create_normal_agent
from contextlib import asynccontextmanager
from typing import Generic, TypeVar, Optional,List
from web_server.class_model import (
    user,
    graph
)
import io
from web_server.service import user_service, file_service, graph_service,redis_listener



def initialize_clients():
    global llm_factory, embedding_factory,embedding_tool     
    try:
        llm_factory = LLMsFactory()
        embedding_tool = get_instance()
    except Exception as e:
        logger.warning(f"Failed to initialize LLM factory: {e}")
        llm_factory = None
    
    try:
        embedding_factory = EmbeddingFactory().create_embedding()
    except Exception as e:
        logger.warning(f"Failed to initialize Embedding factory: {e}")
        embedding_factory = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_clients()
    # 启动 Redis 监听器（后台协程运行）
    await redis_listener.start_listeners()
    yield
    logger.info("应用程序关闭...")

app = FastAPI(lifespan=lifespan)

file_router = APIRouter(prefix="/api/file")
config_router = APIRouter(prefix="/api/config")
llm_react_router = APIRouter(prefix="/api/llm/react")
simila_router = APIRouter(prefix="/api/similarity")
user_router = APIRouter(prefix="/api/user")
graph_router = APIRouter(prefix="/api/graph")
# 注册全局异常处理器
register_exception_handlers(app)

# 配置跨域
setup_cors(app)

# 全局客户端实例
llm_factory = None
embedding_factory = None
embedding_tool = None
T = TypeVar("T")

class BatchSimilarityRequest(BaseModel):
    query: str
    documents: list

class Response(BaseModel, Generic[T]):
    code: int = 0
    message: str = "OK"
    data: Optional[T] = None

### user 路由
@app.get("/heartbeat")
async def heartbeat():
    try:
        rag_system = get_rag_system()
        embedding_tool = get_instance()
        
        return {
            "status": "success",
            "message": "Service is running",
            "components": {
                "neo4j": "connected" if neo4j_client and neo4j_client.graph else "disconnected",
                "rag": "initialized" if rag_system else "not initialized",
                "embedding": "ready" if embedding_tool else "not ready",
                "llm_factory": "ready" if llm_factory else "not ready",
                "embedding_factory": "ready" if embedding_factory else "not ready"
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@user_router.post("/register")
async def register_user(user: user.UserInfoRequest):
    user = user_service.user_register(user)
    if not user:
        return Response(code=886, message="User already exists")
    return Response(data=user)

@user_router.post("/login")
async def login_user(user: user.UserInfoRequest):
    user = user_service.user_login(user)
    if not user:
        return Response(code=886, message="Invalid credentials")
    return Response(data=user)

@user_router.get("/rememberMe")
async def get_user_remember_me(token: str):
    user = user_service.get_user_remember_me(token)
    if not user:
        return Response(code=886, message="User not found")
    return Response(data=user)

### graph 路由
@graph_router.post("/saveOrUpdate/nodes")
async def create_graph_node(nodes: List[graph.graphNode]):
    node = graph_service.saveOrUpdate_graph_nodes(nodes)
    return Response(data=node)

@graph_router.get("/get/nodes")
async def get_graph_nodes():
    nodes = graph_service.get_graph_nodes()
    if not nodes:
        return Response(code=886, message="Nodes not found")
    return Response(data=nodes)

@graph_router.post("/saveOrUpdate/edges")
async def create_graph_edge(edges: List[graph.graphEdge]):
    edge = graph_service.saveOrUpdate_graph_edges(edges)
    return Response(data=edge)

@graph_router.get("/get/edges")
async def get_graph_edges():
    edges = graph_service.get_graph_edges()
    if not edges:
        return Response(code=886, message="Edges not found")
    return Response(data=edges)

### 
@simila_router.post("/documents/similarity")
async def document_similarity(request: BatchSimilarityRequest):
    similarity = embedding_tool.calculate_similarity_batch(request.query,request.documents)
    return {"status": "success", "similarity": similarity}

@file_router.post("/info/analyze")
async def analyze_info(file: UploadFile = File(...)):
    content = await file.read()
    info_chunks = await file_service.get_textchunk_info(content)
    return {"status": "success", "info_chunks": info_chunks}

@config_router.get("/env/configs")
async def get_env_config():
    return {"status": "success", "config": env_config.get_env_config()} 

@llm_react_router.get("/chat/invokeStream")
async def llm_react_invoke(query: str):
    llm = create_normal_agent(react=True)
    response = llm.invoke_agent_stream(query)
    return StreamingResponse(
        content=llm.stream_agent_praser(response),
        media_type="text/event-stream"
    )

# 注册路由（必须在路由定义之后）
app.include_router(file_router)
app.include_router(config_router)
app.include_router(llm_react_router)
app.include_router(simila_router)
app.include_router(user_router)
app.include_router(graph_router)