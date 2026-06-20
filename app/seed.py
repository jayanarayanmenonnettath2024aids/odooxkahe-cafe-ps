import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory, engine, Base
from app.core.security import hash_password
from app.models.category import Category
from app.models.floor import Floor
from app.models.payment_method import PaymentMethod
from app.models.product import Product
from app.models.table import Table, TableStatus
from app.models.user import User, UserRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")


async def seed_db():
    logger.info("Initializing database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        try:
            # Check if admin exists
            from sqlalchemy import select
            admin = await db.execute(select(User).where(User.email == "admin@cafepos.com"))
            if not admin.scalars().first():
                logger.info("Seeding Admin User...")
                db.add(User(
                    name="Admin",
                    email="admin@cafepos.com",
                    password_hash=hash_password("admin123"),
                    role=UserRole.ADMIN
                ))

            # Seeding Cash, Card, UPI payment methods
            payment_methods = await db.execute(select(PaymentMethod))
            if not payment_methods.scalars().first():
                logger.info("Seeding Payment Methods...")
                db.add_all([
                    PaymentMethod(name="CASH", enabled=True),
                    PaymentMethod(name="CARD", enabled=True),
                    PaymentMethod(name="UPI", upi_id="cafepos@upi", enabled=True),
                ])

            # Seed basic categories and products
            categories = await db.execute(select(Category))
            if not categories.scalars().first():
                logger.info("Seeding Categories & Products...")
                hot_drinks = Category(name="Hot Drinks", color="#FF5733")
                cold_drinks = Category(name="Cold Drinks", color="#33A8FF")
                food = Category(name="Food", color="#33FF57")
                db.add_all([hot_drinks, cold_drinks, food])
                await db.flush()

                db.add_all([
                    Product(name="Espresso", description="Strong black coffee", price=3.50, category_id=hot_drinks.id),
                    Product(name="Latte", description="Milky coffee", price=4.50, category_id=hot_drinks.id),
                    Product(name="Iced Tea", description="Refreshing peach iced tea", price=3.00, category_id=cold_drinks.id),
                    Product(name="Croissant", description="Buttery French pastry", price=2.50, category_id=food.id),
                ])

            # Seed Floor and Tables
            floors = await db.execute(select(Floor))
            if not floors.scalars().first():
                logger.info("Seeding Floors & Tables...")
                main_floor = Floor(name="Main Floor")
                patio = Floor(name="Patio")
                db.add_all([main_floor, patio])
                await db.flush()

                db.add_all([
                    Table(table_number="T1", seat_count=2, floor_id=main_floor.id, active_status=TableStatus.AVAILABLE),
                    Table(table_number="T2", seat_count=4, floor_id=main_floor.id, active_status=TableStatus.AVAILABLE),
                    Table(table_number="P1", seat_count=4, floor_id=patio.id, active_status=TableStatus.AVAILABLE),
                ])

            await db.commit()
            logger.info("Database seeding completed successfully.")

        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(seed_db())
