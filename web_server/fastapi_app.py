from fastapi import FastAPI, File, UploadFile, APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from middleware.neo4j_client import Neo4jClient
from utils.rag_system import get_rag_system
from factories.llmsFactory.llms_factory import LLMsFactory
from factories.embeddingFactory.embedding_factory import EmbeddingFactory
from utils.file_convert import convert_file_to_md
from info.analyze_strategy import getTextchunk_info
from web_server.global_handler.exception_handler import register_exception_handlers
from web_server.global_handler.cors_config import setup_cors
from utils.embedding_tool import embedding_instance, get_instance
from utils.llm_prompt.llm_utils import create_normal_agent
import utils.env_config as env_config
from contextlib import asynccontextmanager
import io

def initialize_clients():
    global neo4j_client, llm_factory, embedding_factory,embedding_tool 
    try:
        neo4j_client = Neo4jClient()
    except Exception as e:
        print(f"Warning: Failed to initialize Neo4j client: {e}")
        neo4j_client = None
    
    try:
        llm_factory = LLMsFactory()
        embedding_tool = get_instance()
    except Exception as e:
        print(f"Warning: Failed to initialize LLM factory: {e}")
        llm_factory = None
    
    try:
        embedding_factory = EmbeddingFactory().create_embedding()
    except Exception as e:
        print(f"Warning: Failed to initialize Embedding factory: {e}")
        embedding_factory = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_clients()
    yield
    print("应用程序关闭...")

app = FastAPI(lifespan=lifespan)

file_router = APIRouter(prefix="/api/file")
config_router = APIRouter(prefix="/api/config")
llm_react_router = APIRouter(prefix="/api/llm/react")
simila_router = APIRouter(prefix="/api/similarity")

# 注册全局异常处理器
register_exception_handlers(app)

# 配置跨域
setup_cors(app)

# 全局客户端实例
neo4j_client = None
llm_factory = None
embedding_factory = None
embedding_tool = None

class BatchSimilarityRequest(BaseModel):
    query: str
    documents: list


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


@simila_router.post("/documents/similarity")
async def document_similarity(request: BatchSimilarityRequest):
    similarity = embedding_tool.calculate_similarity_batch(request.query,request.documents)
    return {"status": "success", "similarity": similarity}

@file_router.post("/info/analyze")
async def analyze_info(file: UploadFile = File(...)):
    content = await file.read()
    info_chunks = getTextchunk_info(convert_file_to_md(io.BytesIO(content)))
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
