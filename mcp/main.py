import asyncio
from utils.start_server import *
from fastmcp import FastMCP

mcp = FastMCP("server_name")

@mcp.tool
async def test(text: str):
    """测试"""
    return f"ciallo {text}"

@mcp.tool
async def get_weather():
    return "晴"


async def main():
    await asyncio.gather(
        start_mcp(mcp)
    )

if __name__ == "__main__":
    asyncio.run(main())