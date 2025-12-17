import asyncio
import asyncpg
from asyncpg import Connection

class PostgreClient:
    _instance = None
    sql_connect: Connection

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    async def connect(cls):
        cls.sql_connect = await asyncpg.connect(
            host="192.168.2.118",
            port=5432,
            database="qq_bot",
            user="postgres",
            password="Qqwe123123"
            )
        

async def main() -> None:
    postgre_client = PostgreClient()
    await postgre_client.connect()

    results = await postgre_client.sql_connect.fetch("SELECT * FROM test")
    for i in results:

        print(dict(i))

if __name__ == '__main__':
    asyncio.run(main())