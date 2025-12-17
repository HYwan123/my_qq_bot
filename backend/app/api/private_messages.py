from fastapi import APIRouter, Request
import json 

router = APIRouter()


data_wan = {
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


@router.get('/messages')
async def get_messages(request: Request):
    return json.dumps(request.app.state.messages, ensure_ascii=False)

@router.get('/test')
async def test():
    return {'msg': 'test OK 200'}

@router.post('/test_ws_send')
async def send_hello_to_me():
    await ws_global.send(json.dumps(data_wan)) # type: ignore

@router.post('/ws_send')
async def send_message():
    await ws_global.send(json.dumps(data)) # type: ignore
