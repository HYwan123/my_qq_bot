import aiohttp
import asyncio
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from app.util.mcp_clinet import McpClient

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        )
    
    api_key: str
    api_host: str
    


@lru_cache
def get_settings():
    return Settings() # type: ignore

class OpenaiClient:
    
    _instance = None
    api_key: str = get_settings().api_key
    api_host: str = get_settings().api_host
    mcp_client = McpClient()

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.session_client = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            )

    async def chat(self, messages:list[dict]):
        async with self.session_client.post(self.api_host, json=self.make_message(messages=messages)) as resp:
            return await resp.json()

    async def chat_with_tools(self, messages: list[dict]):
        async with self.session_client.post(self.api_host, json=self.make_message(messages=messages, tools=await self.mcp_client.list_tools_to_dict())) as resp:
            result = await resp.json()
        print(result)
        message = self.get_message(result)
        tool_calls = message.get('tool_calls', [])
        
        if tool_calls:
            first_call = tool_calls[0]
            import json
            args = json.loads(first_call['function']['arguments'])
            function_result = await self.mcp_client.call_tools(first_call['function']['name'], args)
            print(function_result)
            
            # 回填 tool 消息
            tool_message = {
                "role": "assistant",
                "tool_call_id": first_call['id'],
                "content": str(function_result.content[0].text)  # 假设只取第一个文本结果
            }
            print(tool_message)
            # 再次发送给模型
            result = await self.chat([tool_message])
            
        return result


    async def one_chat(self, text: str) -> dict:
        async with self.session_client.post(self.api_host, json=self.make_message(messages=[{"role": "user","content": text}])) as resp:
            return await resp.json()

    async def test(self) -> dict:
        async with self.session_client.post(self.api_host, json=self.make_message()) as resp:
            return await resp.json()
        
    async def close_session(self):
        await self.session_client.close()

    @staticmethod
    def make_message(
            messages: list[dict] = [{"role": "user","content": "test,回复测试成功即可"}],
            model: str = "kimi-k2",
            tools: list = []
            ) -> dict:
    
        payload = {
            "model": model,
            "messages": messages,
            'tools': tools
        }

        return payload

    @staticmethod
    def get_message_content(response_json: dict):
        return response_json['choices'][0]['message']['content']

    @staticmethod
    def get_message(response_json: dict):
        return response_json['choices'][0]['message']

async def main() -> None:

    
    print(get_settings().api_key)
    client = OpenaiClient()
    tools = await client.mcp_client.list_tools_to_dict()
    result = await client.chat_with_tools([{'role': 'system', 'content': '请试着调用工具'},
                                           {"role": "user", "content": "请调用 get_weather 工具获取今天的天气"}])
    print(type(result))
    print(result)
    print(result['choices'][0]['message'])
    await client.close_session()

if __name__ == '__main__':
    asyncio.run(main())