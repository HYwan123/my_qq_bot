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
        while True:
            await asyncio.sleep(1)
            try:
                async for event in AioHttpClient.listen_sse('/_events'):

                    event = extract_event_info(event) # type: ignore
                    print("收到 SSE:", event) # type: ignore
                    data = event['message']
                    if str(event['user_id']) == '3801230796':
                        print('回复人:机器人自己')

                        user = event['target_id']
                        character = 'assistant'
                        if user not in messages:
                            messages[user] = [{'role': 'system', 'content': '你是一个qq聊天机器人,请每句话尽量简短,最好不要超过20个字'}]
                        messages[user].append({'role': character, 'content': data[0]['data']['text']})




                    else:
                        

                        user = event['user_id']
                        print(user)
                        character = 'user'

                        if user not in messages:
                            messages[user] = [{'role': 'system', 'content': '你是一个qq聊天机器人,请每句话尽量简短,最好不要超过20个字'}]
                        messages[user].append({'role': character, 'content': data[0]['data']['text']})
                        print(messages)
                        print('尝试调用')
                        print(messages[user])
                        for _ in range(3):
                            try:
                                response = await openai_client.chat(
                                    messages=messages[user]
                                ) # type: ignore
                                break
                            except Exception as e:
                                print(e)
                        else:
                            continue

                        print(f'尝试完成{response}')
                        choice = openai_client.get_message_content(response)
                        print(choice)
                        global ws_global
                        for _ in range(3):
                            try:
                                ws_global = await send_message_to_user(ws_global, '2801798663', choice) # type: ignore
                                break
                            except Exception as e:
                                print(e)
                                ws_global = await reconnect()
                        else:
                            continue
            except Exception as e:
                print(e)
                    


    
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