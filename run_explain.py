import asyncio
from sqlalchemy import text
from app.core.database import async_session_factory

async def run_explain():
    async with async_session_factory() as session:
        # Example 1: High frequency query (orders by customer)
        res1 = await session.execute(text("EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 1"))
        print("Query 1:", "\n".join([r[0] for r in res1]))
        
        # Example 2: Payments by reference
        res2 = await session.execute(text("EXPLAIN ANALYZE SELECT * FROM payments WHERE transaction_reference = 'ref123'"))
        print("\nQuery 2:", "\n".join([r[0] for r in res2]))

if __name__ == "__main__":
    asyncio.run(run_explain())
