import uvicorn
import os

if __name__ == '__main__':
    uvicorn.run('web_server.fastapi_app:app', host=os.getenv('WEB_SERVER_HOST'), port=int(os.getenv('WEB_SERVER_PORT')), reload=True)
