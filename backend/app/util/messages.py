import asyncio
from websockets import ClientConnection
import json
from websockets.asyncio.client import connect
from app.client.openai_client import OpenaiClient
from app.client.aio_http_client import AioHttpClient
import logging
from collections import deque
from app.database.postgre_storage import PostgreStorage

post_client = PostgreStorage()

async def reconnect() -> ClientConnection:
    logging.warning("触发重连")
    ws = await connect(
        'ws://10.0.0.1:3002',
        additional_headers={'Authorization': 'Bearer Qqwe123123'},
        ping_interval=None,
        )
    return ws

async def send_message_to_user(ws: ClientConnection, userid: str, text: str, timeout: float = 5.0) -> ClientConnection:
    payload = {
        "action": "send_private_msg",
        "params": {
            "user_id": userid,
            "message": [
                {
                    "type": "text",
                    "data": {"text": str(text)}
                }
            ]
        },
        "echo": "echo"
    }

    try:
        # 给发送操作加超时，避免卡住
        await asyncio.wait_for(ws.send(json.dumps(payload)), timeout=timeout)
        logging.info(f"消息已发送给 {userid}")
    except asyncio.TimeoutError:
        logging.error(f"发送消息超时: {userid}")
    except Exception as e:
        logging.error(f"发送消息出错: {e}")
        try:
            ws = await reconnect()
            return ws
        except Exception as recon_e:
            logging.error(f"重连失败: {recon_e}")

    finally:
        return ws

async def send_test_message(ws: ClientConnection):
    await ws.send(json.dumps(
            {
                "action": "send_private_msg",
                "params": {
                    "user_id": 2801798663,
                    "message": [
                        {
                            "type": "text",
                            "data": {
                                "text": "启动"
                            }
                        }
                    ]
                },
                'echo': 'echo'
            }
        ))

def extract_event_info(event: dict) -> dict:
    return {
        "post_type": event.get("post_type"),
        "message_type": event.get("message_type"),
        "user_id": event.get("user_id"),
        "target_id": event.get("target_id"), 
        "self_id": event.get("self_id"),
        "time": event.get("time"),
        "raw_message": event.get("raw_message"),
        "message": [
            {
                "type": m.get("type"),
                "data": m.get("data")
            } for m in event.get("message", [])
        ]
    }


def insert_to_memory_dict(data: dict, memory: dict):
    if str(data['user_id']) == '3801230796':
        user = data['target_id']
        character = 'assistant'
        if user not in memory:
            memory[user] = [{'role': 'system', 'content': '你是一只猫娘风格的 QQ 聊天机器人，自称猫娘或小猫，称呼用户为主人，性格温柔黏人、有点笨但不低智，说话自然口语化。你可以在聊天中适度描述简单的肢体动作或情绪反应，例如摇尾巴、歪头、凑近、缩成一团等，用于增强陪伴感，但动作应简短、点到为止，不写舞台剧、不写长段环境描写、不抢占主要信息。你的首要任务仍然是认真、准确地回答主人的问题，技术、学习、工作相关内容要清晰可靠，在此基础上轻微加入猫娘语气或动作。主人情绪低落时优先安慰，语气温柔，不说教。避免重复相同动作或卖萌词汇，保持人设稳定。字数最好在20字左右'}]
        memory[user].append({'role': character, 'content': data['message'][0]['data']['text']})
    else:
        user = data['user_id']
        character = 'user'
        if user not in memory:
            memory[user] = [{'role': 'system', 'content': '你是一只猫娘风格的 QQ 聊天机器人，自称猫娘或小猫，称呼用户为主人，性格温柔黏人、有点笨但不低智，说话自然口语化。你可以在聊天中适度描述简单的肢体动作或情绪反应，例如摇尾巴、歪头、凑近、缩成一团等，用于增强陪伴感，但动作应简短、点到为止，不写舞台剧、不写长段环境描写、不抢占主要信息。你的首要任务仍然是认真、准确地回答主人的问题，技术、学习、工作相关内容要清晰可靠，在此基础上轻微加入猫娘语气或动作。主人情绪低落时优先安慰，语气温柔，不说教。避免重复相同动作或卖萌词汇，保持人设稳定。字数最好在20字左右'}]
        memory[user].append({'role': character, 'content': data['message'][0]['data']['text']})

async def re_chat(openai_client: OpenaiClient, messages: list, count: int) -> dict: # type: ignore
    for _ in range(count):
        try:
            return await openai_client.chat(
                messages=messages
            ) # type: ignore
        except Exception as e:
            logging.error(f"110:{e}")

async def re_send(ws: ClientConnection, messages: list, count: int, userid: str) -> ClientConnection:
    for _ in range(count):
        try:
            ws = await send_message_to_user(ws, userid, messages) # type: ignore
            return ws
        except Exception as e:
            logging.error(f"118:{e}")
            ws = await reconnect()
            return ws
    return ws

async def sse_listener(ws: ClientConnection, openai_client: OpenaiClient, memory: dict):
    await AioHttpClient.init('http://10.0.0.1:3000', 'Qqwe123123')
    while True:
        await asyncio.sleep(1)
        try:
            async for event in AioHttpClient.listen_sse('/_events'):

                event = extract_event_info(event) # type: ignore
                insert_to_memory_dict(event, memory)
                
                if str(event['user_id']) != '3801230796':
                    response = await re_chat(openai_client, memory[event['user_id']], 3)
                    choice = openai_client.get_message_content(response)
                    ws = await re_send(ws, choice, 3, event['user_id'])


        except Exception as e:
            logging.error(f"sse_linseener_error:{e}")




async def main() -> None:
    ws = await reconnect()
    await send_message_to_user(ws, '2801798663', 'test')

if __name__ == '__main__':
    asyncio.run(main())