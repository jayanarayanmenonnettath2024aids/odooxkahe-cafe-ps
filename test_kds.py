import asyncio
from app.core.database import async_session_factory
from app.services.kds_service import KDSService
from app.models.customer import Customer
from app.models.pos_session import PosSession
from app.models.user import User

async def test():
    db = async_session_factory()
    service = KDSService(db)
    orders = await service.get_kitchen_orders()
    for o in orders:
        print(o.model_dump_json())
    await db.close()

asyncio.run(test())
