import aiohttp
import asyncio
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


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
            ) -> dict:
    
        payload = {
            "model": model,
            "messages": messages,
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
    result = await client.test()
    print(type(result))
    print(result['choices'][0]['message'])
    await client.close_session()

if __name__ == '__main__':
    asyncio.run(main())