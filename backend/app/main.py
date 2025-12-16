from fastapi import FastAPI
import uvicorn
import asyncio
from app.api.private_messages import router
from contextlib import asynccontextmanager
from websockets.asyncio.client import connect
from app.util.messages import *
from app.util.aio_http_client import AioHttpClient
import aiohttp
from typing import Dict, List, Any
from app.util.openai_client import OpenaiClient
from app.model.chat import *

ws_global: ClientConnection = None # type: ignore
messages: Dict[str, List[Any]] = {}



@asynccontextmanager
async def lifespan(app: FastAPI):
    openai_client = OpenaiClient()
    result = await openai_client.test()
    print(result)
    global ws_global
    ws_global = await connect(
        'ws://10.0.0.1:3002',
        additional_headers={'Authorization': 'Bearer Qqwe123123'},
        ping_interval=None,
        )  # 启动逻辑
    
    sse_task = asyncio.create_task(sse_listener(ws_global, openai_client, messages))

    print("启动")
    yield
    await AioHttpClient.close()
    sse_task.cancel()
    # 关闭逻辑
    print("关闭")

app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/private")


async def main() -> None:
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=15433,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())