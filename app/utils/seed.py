"""
Seed data script — populates the database with initial data.

Run: python -m app.utils.seed
"""

import asyncio
import uuid

from app.core.database import async_session_factory, engine, Base
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.category import Category
from app.models.product import Product
from app.models.floor import Floor
from app.models.table import Table
from app.models.payment_method import PaymentMethod
from app.models.coupon import Coupon
from app.models.promotion import Promotion
from app.models.coupon import DiscountType
from app.models.promotion import PromotionScope, PromotionDiscountType

from datetime import date, timedelta


async def seed():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        # ── Users ──────────────────────────────────────────────
        admin = User(
            name="Admin User",
            email="admin@cafepos.com",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN,
        )
        emp1 = User(
            name="John Barista",
            email="john@cafepos.com",
            password_hash=hash_password("employee123"),
            role=UserRole.EMPLOYEE,
        )
        emp2 = User(
            name="Jane Server",
            email="jane@cafepos.com",
            password_hash=hash_password("employee123"),
            role=UserRole.EMPLOYEE,
        )
        session.add_all([admin, emp1, emp2])

        # ── Customers ─────────────────────────────────────────
        customers = [
            Customer(name="Walk-in Customer", email="walkin@cafepos.com", phone="0000000000"),
            Customer(name="Rahul Sharma", email="rahul@example.com", phone="9876543210"),
            Customer(name="Priya Patel", email="priya@example.com", phone="9876543211"),
        ]
        session.add_all(customers)

        # ── Categories ────────────────────────────────────────
        categories = [
            Category(name="Hot Beverages", color="#D4451A"),
            Category(name="Cold Beverages", color="#1A8BD4"),
            Category(name="Snacks", color="#D4A81A"),
            Category(name="Main Course", color="#1AD44A"),
            Category(name="Desserts", color="#D41A8B"),
            Category(name="Sides", color="#8B1AD4"),
        ]
        session.add_all(categories)
        await session.flush()

        # ── Products ──────────────────────────────────────────
        products = [
            # Hot Beverages
            Product(name="Espresso", description="Rich single shot espresso", price=120, tax_percentage=5, category_id=categories[0].id),
            Product(name="Cappuccino", description="Classic Italian cappuccino", price=180, tax_percentage=5, category_id=categories[0].id),
            Product(name="Latte", description="Smooth café latte", price=200, tax_percentage=5, category_id=categories[0].id),
            Product(name="Americano", description="Espresso with hot water", price=150, tax_percentage=5, category_id=categories[0].id),
            Product(name="Hot Chocolate", description="Rich Belgian hot chocolate", price=220, tax_percentage=5, category_id=categories[0].id),
            Product(name="Green Tea", description="Japanese green tea", price=140, tax_percentage=5, category_id=categories[0].id),

            # Cold Beverages
            Product(name="Iced Latte", description="Cold espresso with milk", price=220, tax_percentage=5, category_id=categories[1].id),
            Product(name="Cold Brew", description="Smooth cold brewed coffee", price=250, tax_percentage=5, category_id=categories[1].id),
            Product(name="Mango Smoothie", description="Fresh mango smoothie", price=280, tax_percentage=5, category_id=categories[1].id),
            Product(name="Fresh Orange Juice", description="Freshly squeezed", price=180, tax_percentage=5, category_id=categories[1].id),
            Product(name="Iced Tea", description="Refreshing iced tea", price=160, tax_percentage=5, category_id=categories[1].id),

            # Snacks
            Product(name="Croissant", description="Butter croissant", price=120, tax_percentage=12, category_id=categories[2].id),
            Product(name="Chocolate Muffin", description="Double chocolate muffin", price=150, tax_percentage=12, category_id=categories[2].id),
            Product(name="Veg Sandwich", description="Grilled veg sandwich", price=180, tax_percentage=12, category_id=categories[2].id),
            Product(name="Paneer Wrap", description="Spicy paneer wrap", price=220, tax_percentage=12, category_id=categories[2].id),

            # Main Course
            Product(name="Pasta Alfredo", description="Creamy pasta alfredo", price=350, tax_percentage=12, category_id=categories[3].id),
            Product(name="Margherita Pizza", description="Classic thin crust pizza", price=400, tax_percentage=12, category_id=categories[3].id),
            Product(name="Club Sandwich", description="Triple decker club sandwich", price=320, tax_percentage=12, category_id=categories[3].id),

            # Desserts
            Product(name="Cheesecake", description="New York cheesecake", price=280, tax_percentage=12, category_id=categories[4].id),
            Product(name="Brownie", description="Warm chocolate brownie", price=200, tax_percentage=12, category_id=categories[4].id),
            Product(name="Tiramisu", description="Classic Italian tiramisu", price=320, tax_percentage=12, category_id=categories[4].id),

            # Sides
            Product(name="French Fries", description="Crispy golden fries", price=150, tax_percentage=12, category_id=categories[5].id),
            Product(name="Garlic Bread", description="Cheesy garlic bread", price=180, tax_percentage=12, category_id=categories[5].id),
        ]
        session.add_all(products)

        # ── Floors ────────────────────────────────────────────
        floors = [
            Floor(name="Ground Floor"),
            Floor(name="First Floor"),
            Floor(name="Terrace"),
        ]
        session.add_all(floors)
        await session.flush()

        # ── Tables ────────────────────────────────────────────
        tables = []
        for floor in floors:
            for i in range(1, 7):
                tables.append(Table(
                    floor_id=floor.id,
                    table_number=f"T{floor.id}{i:02d}",
                    seat_count=2 if i <= 2 else (4 if i <= 4 else 6),
                    unique_token=str(uuid.uuid4()),
                ))
        session.add_all(tables)

        # ── Payment Methods ───────────────────────────────────
        payment_methods = [
            PaymentMethod(name="CASH", enabled=True),
            PaymentMethod(name="CARD", enabled=True),
            PaymentMethod(name="UPI", enabled=True, upi_id="cafepos@upi"),
        ]
        session.add_all(payment_methods)

        # ── Coupons ───────────────────────────────────────────
        coupons = [
            Coupon(code="WELCOME10", discount_type=DiscountType.PERCENTAGE, discount_value=10, expiry_date=date.today() + timedelta(days=90)),
            Coupon(code="FLAT50", discount_type=DiscountType.FIXED, discount_value=50, expiry_date=date.today() + timedelta(days=60)),
            Coupon(code="COFFEE20", discount_type=DiscountType.PERCENTAGE, discount_value=20, expiry_date=date.today() + timedelta(days=30)),
        ]
        session.add_all(coupons)

        # ── Promotions ────────────────────────────────────────
        promotions = [
            Promotion(
                name="Buy 3+ items, get 10% off",
                promotion_scope=PromotionScope.ORDER,
                minimum_quantity=3,
                discount_type=PromotionDiscountType.PERCENTAGE,
                discount_value=10,
            ),
            Promotion(
                name="Orders above ₹500, get ₹75 off",
                promotion_scope=PromotionScope.ORDER,
                minimum_order_amount=500,
                discount_type=PromotionDiscountType.FIXED,
                discount_value=75,
            ),
        ]
        session.add_all(promotions)

        await session.commit()

        print("✅ Seed data inserted successfully!")
        print(f"   Admin: admin@cafepos.com / admin123")
        print(f"   Employee: john@cafepos.com / employee123")
        print(f"   Products: {len(products)}")
        print(f"   Tables: {len(tables)}")
        print(f"   Coupons: WELCOME10, FLAT50, COFFEE20")


if __name__ == "__main__":
    asyncio.run(seed())
