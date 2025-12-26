import aiohttp
import asyncio
import json

class AioHttpClient:
    _session: aiohttp.ClientSession | None = None
    _base_url: str = ""
    _token: str | None = None

    @classmethod
    async def init(cls, base_url: str, token: str | None = None):
        """初始化全局 session"""
        cls._base_url = base_url.rstrip("/")
        cls._token = token
        if cls._session is None:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            cls._session = aiohttp.ClientSession(headers=headers)

    @classmethod
    async def close(cls):
        """关闭全局 session"""
        if cls._session:
            await cls._session.close()
            cls._session = None

    @classmethod
    async def get(cls, path: str, params: dict | None = None):
        url = f"{cls._base_url}{path}"
        async with cls._session.get(url, params=params) as resp: # type: ignore
            resp.raise_for_status()
            return await resp.json()

    @classmethod
    async def post(cls, path: str, data: dict | None = None):
        url = f"{cls._base_url}{path}"
        async with cls._session.post(url, json=data) as resp: # type: ignore
            resp.raise_for_status()
            return await resp.json()

    @classmethod
    async def listen_sse(cls, path: str):
        url = f"{cls._base_url}{path}"
        async with cls._session.get(url) as resp: # type: ignore
            buffer = ""
            async for chunk in resp.content.iter_any():
                chunk = chunk.decode()
                buffer += chunk
                while "\n\n" in buffer:
                    line, buffer = buffer.split("\n\n", 1)
                    if line.startswith("data: "):
                        data = line[6:]
                        try:
                            yield json.loads(data)
                        except json.JSONDecodeError:
                            yield data
