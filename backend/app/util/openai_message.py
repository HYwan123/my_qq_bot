def make_payload(
    content: str = "test,回复测试成功即可",
    model: str = "kimi-k2",
) -> dict:
    """生成请求 payload，未提供参数使用默认值"""
    

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
    }

    return payload
