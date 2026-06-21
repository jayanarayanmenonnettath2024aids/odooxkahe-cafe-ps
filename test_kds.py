import asyncio
from app.core.database import async_session_factory
from app.services.kds_service import KDSService
from app.models.pos_session import PosSession
from app.models.order import Order

async def test():
    async with async_session_factory() as db:
        service = KDSService(db)
        orders = await service.get_kitchen_orders()
        print("KDS Orders:")
        for o in orders:
            print(f"- ID: {o.id}, Number: {o.order_number}, Status: {o.status.value}, Type: {o.order_type}")

if __name__ == "__main__":
    asyncio.run(test())
