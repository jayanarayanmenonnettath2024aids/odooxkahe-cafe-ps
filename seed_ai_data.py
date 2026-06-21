import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_factory, engine
from app.models.payment import Payment
from app.models.reservation import Reservation
from app.models.refresh_token import RefreshToken
from app.models.snapshot import OrderSnapshot, PaymentSnapshot, ReservationSnapshot, DailySalesSnapshot
from app.models.order_version import OrderVersion
from app.models.analytics_mirror import OrdersAnalytics, PaymentsAnalytics, ReservationsAnalytics, CustomerAnalytics
from app.models.store_setting import StoreSetting
from app.models.inventory import InventoryItem
from app.models.feedback import Feedback
from app.models.pos_session import PosSession
from app.models.user import User
from app.models.table import Table
from app.models.floor import Floor
from app.models.coupon import Coupon
from app.models.promotion import Promotion
from app.models.payment_method import PaymentMethod
from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.category import Category

async def seed_ai_data():
    async with async_session_factory() as session:
        # Seed Inventory
        inventory_items = [
            InventoryItem(name="Coffee Beans", current_stock=12.5, minimum_stock=5.0, reorder_level=10.0, unit="kg"),
            InventoryItem(name="Milk", current_stock=4.0, minimum_stock=5.0, reorder_level=15.0, unit="L"),
            InventoryItem(name="Sugar", current_stock=20.0, minimum_stock=10.0, reorder_level=25.0, unit="kg"),
            InventoryItem(name="Chocolate Syrup", current_stock=8.0, minimum_stock=2.0, reorder_level=5.0, unit="L"),
            InventoryItem(name="Burger Buns", current_stock=50.0, minimum_stock=20.0, reorder_level=100.0, unit="unit"),
            InventoryItem(name="Tea Leaves", current_stock=5.0, minimum_stock=2.0, reorder_level=8.0, unit="kg"),
        ]
        
        session.add_all(inventory_items)

        # Seed Feedback
        now = datetime.now(timezone.utc)
        feedbacks = [
            Feedback(rating=5, comment="Great coffee, very fast service!", created_at=now - timedelta(days=1)),
            Feedback(rating=4, comment="Good ambience, but brownie was a bit dry.", created_at=now - timedelta(days=2)),
            Feedback(rating=5, comment="Excellent burger and amazing fries.", created_at=now - timedelta(days=3)),
            Feedback(rating=2, comment="Waiting time was too slow today.", created_at=now - timedelta(days=4)),
            Feedback(rating=1, comment="Cold coffee was literally warm, very bad.", created_at=now - timedelta(days=5)),
            Feedback(rating=5, comment="Friendly staff and fresh food.", created_at=now - timedelta(days=6)),
            Feedback(rating=4, comment="Nice place, tasty tea.", created_at=now - timedelta(days=7)),
            Feedback(rating=5, comment="Amazing coffee, clean tables.", created_at=now - timedelta(days=8)),
            Feedback(rating=3, comment="A bit expensive but okay.", created_at=now - timedelta(days=9)),
            Feedback(rating=5, comment="Fast service, excellent experience.", created_at=now - timedelta(days=10)),
        ]
        
        session.add_all(feedbacks)
        
        await session.commit()
        print("AI data seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_ai_data())
