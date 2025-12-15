from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam
import asyncio
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        )
    
    api_key: str
    


@lru_cache
def get_settings():
    return Settings() # type: ignore

class OpenaiClient:

    _instance = None
    conn = AsyncOpenAI(
        base_url='https://apis.iflow.cn/v1',
        timeout=999999999,
        api_key=get_settings().api_key
        )

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)

        print(get_settings().api_key)
        return cls._instance


    @classmethod
    async def get_client(cls):
        return cls.conn

    @classmethod
    async def test(cls):
        return await cls.conn.chat.completions.create(
            model='Qwen3-Max',
            messages=[
                ChatCompletionSystemMessageParam(role="system", content="test")
                
                ]
            
            )
        

async def main() -> None:
    print(get_settings().api_key)
    client = OpenaiClient()
    result = await client.test()
    print(result)

if __name__ == '__main__':
    asyncio.run(main())