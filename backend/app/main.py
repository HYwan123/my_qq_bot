from fastapi import FastAPI
import uvicorn
import asyncio
from app.api.private_messages import router
from app.util.messages import *
from app.model.chat import *
from app.core.lifespan import lifespan


app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/private")

async def main() -> None:
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=15433,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())