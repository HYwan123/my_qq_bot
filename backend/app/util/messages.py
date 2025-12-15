from websockets import ClientConnection
import json
async def send_message_to_user(ws: ClientConnection, text: str, userid: int):
    await ws.send(json.dumps(
        {
            "action": "send_private_msg",
            "params": {
                "user_id": userid,
                "message": [
                    {
                        "type": "text",
                        "data": {
                            "text": str(text)
                        }
                    }
                ]
            },
            'echo': 'echo'
        }
        ))

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

def main() -> None:
    pass
if __name__ == '__main__':
    main()