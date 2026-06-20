import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check():
    engine = create_async_engine("postgresql+asyncpg://postgres:runtime@localhost:5432/postgres")
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='orders';"))
        print([r[0] for r in res.fetchall()])

asyncio.run(check())
