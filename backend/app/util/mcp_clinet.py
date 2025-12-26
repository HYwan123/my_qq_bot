import asyncio
from fastmcp import Client
import json


class McpClient():
    _instance = None
    url = "http://localhost:15441/mcp"
    is_connected = False
    client: Client | None = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, url=None):
        if url is not None:
            McpClient.url = url
            McpClient.client = Client(url)

    @classmethod
    async def connect(cls):
        if cls.client is None:
            cls.client = Client(cls.url)
            await cls.client.__aenter__() 

    @classmethod
    async def list_tools(cls):
        if cls.client is None:
            await cls.connect()
        assert cls.client is not None
        return await cls.client.list_tools_mcp()
        
    @classmethod
    async def list_tools_to_dict(cls) -> list:
        if cls.client is None:
            await cls.connect()
        assert cls.client is not None
        data = await cls.client.list_tools_mcp()
        tools = data.model_dump()['tools']
        result = []
        for tool in tools:
            tmp = {}
            tmp['type'] = 'function'
            tmp['function'] = {}
            tmp['function']['description'] = tool['description']
            tmp['function']['name'] = tool['name']
            tmp['function']['parameters'] = tool['inputSchema']
            tmp['function']['strict'] = True
            result.append(tmp)
        return result
        

    @classmethod
    async def call_tools(cls, function_name: str, data: dict):   
        if cls.client is None:
            await cls.connect()
        else: 
            return await cls.client.call_tool(function_name, data)

    @classmethod
    async def ciallo_test(cls):

        # 调用 MCP 工具
        result = await cls.call_tools("test", {"text": "world!"})
        return result



async def main() -> None:
    mcp_client = McpClient()
    await mcp_client.connect()
    print("初始化完成")
    tools = await mcp_client.list_tools_to_dict()
    test_text = await mcp_client.ciallo_test()
    print(f"tools:{tools}\ntest_text:{test_text}")


if __name__ == '__main__':
    asyncio.run(main())





