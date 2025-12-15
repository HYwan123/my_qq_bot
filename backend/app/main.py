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
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam

ws_global = None
messages: Dict[str, List[Any]] = {}



@asynccontextmanager
async def lifespan(app: FastAPI):
    openai_client = OpenaiClient()
    result = await openai_client.test()
    print(result)
    global ws_global
    ws_global = await connect(
        'ws://10.0.0.1:3002',
        additional_headers={'Authorization': 'Bearer Qqwe123123'}
        )  # 启动逻辑


    await AioHttpClient.init('http://10.0.0.1:3000', 'Qqwe123123')

    async def sse_listener():
        async for event in AioHttpClient.listen_sse('/_events'):
            event = extract_event_info(event) # type: ignore
            print("收到 SSE:", event) # type: ignore
            if event['user_id'] == '3801230796':
                user = event['target_id']
                character = 'assistant'
            else:
                user = event['user_id']
                character = 'user'
            data = event['message']
            if user not in messages:
                messages[user] = []
            messages[user].append({character: data})
            print(messages)
            conn = await openai_client.get_client()
            print('尝试调用')
            print(messages[user])
            response = await conn.chat.completions.create(
                model='kimi-k2',
                messages=[
                ChatCompletionSystemMessageParam(role="system", content="test")
                
                ]
            ) # type: ignore
            print(f'尝试完成{response}')
            choice = response.choices[0]
            print(choice)
            await send_message_to_user(ws_global, 2801798663, choice) # type: ignore


    sse_task = asyncio.create_task(sse_listener())

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