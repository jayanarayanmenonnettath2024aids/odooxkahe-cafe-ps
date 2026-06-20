import asyncio
import asyncpg

async def test():
    try:
        conn = await asyncpg.connect(user='postgres', password='runtime', host='localhost', port=5432, database='postgres')
        print("Connected to postgres:runtime!")
        await conn.close()
    except Exception as e:
        print("postgres:runtime failed:", e)
        
    try:
        conn = await asyncpg.connect(user='postgres', password='runtime', host='localhost', port=5432, database='cafepos_db')
        print("Connected to cafepos_db!")
        await conn.close()
    except Exception as e:
        print("cafepos_db failed:", e)

if __name__ == "__main__":
    asyncio.run(test())
