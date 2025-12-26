async def start_mcp(mcp):
    await mcp.run_async(
        transport="http",
        host="0.0.0.0",
        port=15441,   # MCP 专用端口
    )
