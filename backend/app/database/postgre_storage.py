import asyncio
import asyncpg
from asyncpg import Connection
import logging
from asyncpg import Pool
from typing import cast

class PostgreStorage:
    _instance = None
    pool: Pool


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    async def connect(cls):
        try:
            cls.pool = await asyncpg.create_pool(
                host="192.168.2.118",
                port=5432,
                database="qq_bot",
                user="postgres",
                password="Qqwe123123"
                )
        except Exception as e:
            logging.error(f"连接postgre出错{e}")
            raise

    @classmethod
    async def table_exists(cls, schema: str, table: str) -> bool:
        last_exc = None
        for _ in range(3):
            try:
                async with cls.pool.acquire() as conn:
                    conn = cast(Connection, conn)
                    return await conn.fetchval("SELECT to_regclass($1)", f"{schema}.{table}") is not None
            except Exception as e:
                last_exc = e
                logging.error(f'检查表时出错{e},尝试重连')
                await cls.connect()
        raise last_exc #type: ignore
    
    
    @classmethod
    async def execute(cls, sql: str, *args) -> None:
        last_exc = None
        for _ in range(3):
            try:
                async with cls.pool.acquire() as conn:
                    conn = cast(Connection, conn)
                    await conn.execute(sql, *args)
                return
            except Exception as e:
                last_exc = e
                logging.error(f'检查表时出错{e},尝试重连')
                await cls.connect()
        raise last_exc #type: ignore
    
    @classmethod
    async def fetch(cls, sql: str, *args):
        last_exc = None
        for _ in range(3):
            try:
                async with cls.pool.acquire() as conn:
                    conn = cast(Connection, conn)
                    return await conn.fetch(sql, *args)
            except Exception as e:
                last_exc = e
                logging.error(f'检查表时出错{e},尝试重连')
                await cls.connect()
        raise last_exc #type: ignore

    @classmethod
    async def create_user(cls, user_id: str, username: str):
        await cls.execute("""
                    INSERT INTO core.users (qq_id, name)
                    VALUES ($1, $2)
                    """, user_id, username)

    @classmethod
    async def insert_message(cls, user_id: str, role: str, content: str):
        await cls.execute("""
                    INSERT INTO core.messages(qqid, role, content)
                    VALUES ($1, $2, $3)
                    """, user_id, role, content)
    
    @classmethod
    async def get_message(cls, user_id: str, count: int):
        if count > 0:
            return await cls.fetch(
                """
                SELECT role, content
                FROM core.messages
                WHERE qqid = $1
                ORDER BY id DESC
                LIMIT $2
                """,
                user_id,
                count
            )
        else:
            return await cls.fetch(
                """
                SELECT role, content
                FROM core.messages
                WHERE qqid = $1
                ORDER BY id DESC
                """,
                user_id
            )
        

        
async def main() -> None:
    postgre_client = PostgreStorage()
    await postgre_client.connect()

    result = await postgre_client.table_exists('public', 'test1')
    print(result)

if __name__ == '__main__':
    asyncio.run(main())