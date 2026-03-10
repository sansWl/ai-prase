# 1.创立.env文件，配置
```text
#Web server configuration
WEB_SERVER_HOST=0.0.0.0
WEB_SERVER_PORT=8000
# Embedding configuration
EMBEDDING_TYPE=ollama
# EMBEDDING_MODEL=text-embedding-3-small
OLLAMA_EMBEDDING_MODEL=embeddinggemma:300m
LLM_TYPE=openai
OPENAI_API_KEY=xxxxx
OPENAI_MODEL=deepseek-chat
# OPENAI_TEMPERATURE=0.7
OPENAI_BASE_URL=https://api.deepseek.com/v1
```
# 2.依据webserver/fastapi 的接口
> fastapi接口提供了文本比较、ai-agent stream 流式处理等处理参考
