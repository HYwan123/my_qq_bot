import asyncio
import psycopg
from psycopg import AsyncConnection

class PostgreClient:
    _instance = None
    sql_connect: AsyncConnection

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    async def connect(cls):
        cls.sql_connect = await psycopg.AsyncConnection.connect(
            host="192.168.2.118",
            port=5432,
            dbname="qq_bot",
            user="postgres",
            password="Qqwe123123"
            )
        

async def main() -> None:
    postgre_client = PostgreClient()
    await postgre_client.connect()
    async with postgre_client.sql_connect.cursor() as cursor:
        await cursor.execute("SELECT * FROM test")
        await cursor.fetchall()
        async for result in cursor:
            print(result)


if __name__ == '__main__':
    asyncio.run(main())