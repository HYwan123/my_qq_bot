import asyncio
from websockets import ClientConnection
import json
from websockets.asyncio.client import connect

from app.util.aio_http_client import AioHttpClient

async def reconnect() -> ClientConnection:
    print("触发重连")
    ws = await connect(
        'ws://10.0.0.1:3002',
        additional_headers={'Authorization': 'Bearer Qqwe123123'}
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
        print(f"消息已发送给 {userid}")
    except asyncio.TimeoutError:
        print(f"发送消息超时: {userid}")
    except Exception as e:
        print(f"发送消息出错: {e}")
        try:
            ws = await reconnect()
            return ws
        except Exception as recon_e:
            print(f"重连失败: {recon_e}")

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


def insert_to_memory_dict(data: dict):
    pass

async def main() -> None:
    ws = await reconnect()
    await send_message_to_user(ws, 2801798663, 'test')

if __name__ == '__main__':
    asyncio.run(main())