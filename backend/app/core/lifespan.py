from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager
from websockets.asyncio.client import connect
from app.util.messages import *
from app.client.aio_http_client import AioHttpClient
from app.client.openai_client import OpenaiClient
from typing import Dict, List, Any, cast

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.message = cast(dict[str, list[Any]], {})
    app.state.ws_global = cast(ClientConnection | None, None)
    app.state.message_cursor= cast(Dict[str, int], {})
    openai_client = OpenaiClient()
    result = await openai_client.test()
    print(result)
    global ws_global
    ws_global = await connect(
        'ws://10.0.0.1:3002',
        additional_headers={'Authorization': 'Bearer Qqwe123123'},
        ping_interval=None,
        )  # 启动逻辑
    
    sse_task = asyncio.create_task(sse_listener(ws_global, openai_client, app.state.message))

    print("启动")
    yield
    await AioHttpClient.close()
    sse_task.cancel()
    # 关闭逻辑
    print("关闭")