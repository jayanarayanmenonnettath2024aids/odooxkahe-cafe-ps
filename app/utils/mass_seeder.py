"""
Massive Data Seeder Script for Production-Scale Demo
Populates the database with historical and active orders, multiple floors, large menus, customers, reservations, and more.
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta, timezone, date

from app.core.database import async_session_factory, engine, Base
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.category import Category
from app.models.product import Product
from app.models.floor import Floor
from app.models.table import Table, TableStatus
from app.models.payment_method import PaymentMethod
from app.models.coupon import Coupon, DiscountType
from app.models.promotion import Promotion, PromotionScope, PromotionDiscountType
from app.models.pos_session import PosSession, SessionStatus
from app.models.order import Order, OrderItem, OrderStatus, OrderType, KitchenStatus
from app.models.payment import Payment, PaymentStatus
from app.models.reservation import Reservation, ReservationStatus, ReservationSource
from app.models.order_version import OrderVersion
from app.models.refresh_token import RefreshToken
from app.models.analytics_mirror import OrdersAnalytics, PaymentsAnalytics, ReservationsAnalytics, CustomerAnalytics
from app.models.snapshot import OrderSnapshot, PaymentSnapshot, ReservationSnapshot, DailySalesSnapshot

async def reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def seed_massive_data():
    await reset_db()

    async with async_session_factory() as session:
        print("Starting massive data seed...")

        # 1. Users
        users = [
            User(name="System Admin", email="admin@cafepos.com", password_hash=hash_password("admin123"), role=UserRole.ADMIN),
            User(name="Manager Mike", email="manager@cafepos.com", password_hash=hash_password("manager123"), role=UserRole.EMPLOYEE),
            User(name="Cashier Chloe", email="chloe@cafepos.com", password_hash=hash_password("emp123"), role=UserRole.EMPLOYEE),
            User(name="Waiter Will", email="will@cafepos.com", password_hash=hash_password("emp123"), role=UserRole.EMPLOYEE),
            User(name="Chef Charlie", email="charlie@cafepos.com", password_hash=hash_password("emp123"), role=UserRole.EMPLOYEE),
        ]
        session.add_all(users)
        await session.flush()
        
        # 2. Customers (Generate 50 random customers)
        customers = []
        first_names = ["Rahul", "Priya", "Amit", "Neha", "Vikram", "Sneha", "Karan", "Pooja", "Arjun", "Riya", "Rohan", "Anjali"]
        last_names = ["Sharma", "Patel", "Singh", "Verma", "Kumar", "Gupta", "Das", "Joshi", "Chopra", "Malhotra"]
        for i in range(50):
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            customers.append(Customer(
                name=f"{fn} {ln}",
                email=f"{fn.lower()}.{ln.lower()}{i}@example.com",
                phone=f"98{random.randint(10000000, 99999999)}"
            ))
        session.add_all(customers)
        await session.flush()

        # 3. Floors & Tables
        floors = [Floor(name="Ground Floor"), Floor(name="First Floor"), Floor(name="Rooftop")]
        session.add_all(floors)
        await session.flush()

        tables = []
        for f in floors:
            num_tables = 15 if f.name == "Ground Floor" else 10
            for i in range(1, num_tables + 1):
                tables.append(Table(
                    floor_id=f.id,
                    table_number=f"{f.name[0]}{i}",
                    seat_count=random.choice([2, 4, 6, 8]),
                    active_status=TableStatus.AVAILABLE,
                    unique_token=str(uuid.uuid4())
                ))
        session.add_all(tables)
        await session.flush()

        # 4. Categories & Products
        categories_data = [
            ("Hot Beverages", "#D4451A", ["Espresso", "Cappuccino", "Latte", "Americano", "Mocha", "Macchiato", "Hot Chocolate", "Matcha Latte", "Chai Tea", "Earl Grey"]),
            ("Cold Beverages", "#1A8BD4", ["Iced Latte", "Cold Brew", "Frappuccino", "Iced Tea", "Lemonade", "Mango Smoothie", "Berry Shake", "Cold Coffee", "Orange Juice"]),
            ("Breakfast", "#D4A81A", ["Pancakes", "Waffles", "Avocado Toast", "French Toast", "Omelette", "Eggs Benedict", "Bagel", "Croissant", "Muffin"]),
            ("Mains", "#1AD44A", ["Margherita Pizza", "Pepperoni Pizza", "Pasta Alfredo", "Pasta Arrabiata", "Veg Burger", "Chicken Burger", "Club Sandwich", "Caesar Salad"]),
            ("Desserts", "#D41A8B", ["Cheesecake", "Brownie", "Tiramisu", "Ice Cream Sundae", "Apple Pie", "Chocolate Lava Cake", "Donut", "Macaron"]),
            ("Add-ons", "#8B1AD4", ["Extra Shot", "Almond Milk", "Oat Milk", "Vanilla Syrup", "Caramel Syrup", "Extra Cheese", "French Fries", "Garlic Bread"]),
        ]
        
        categories = []
        products = []
        for cat_name, color, prod_names in categories_data:
            cat = Category(name=cat_name, color=color)
            session.add(cat)
            await session.flush()
            categories.append(cat)
            
            for p_name in prod_names:
                products.append(Product(
                    name=p_name,
                    description=f"Delicious {p_name}",
                    price=random.randint(100, 500),
                    tax_percentage=random.choice([5, 12, 18]),
                    category_id=cat.id,
                    is_active=True
                ))
        session.add_all(products)
        await session.flush()

        # 5. Payment Methods
        payment_methods = [
            PaymentMethod(name="CASH", enabled=True),
            PaymentMethod(name="CARD", enabled=True),
            PaymentMethod(name="UPI", enabled=True, upi_id="pay@cafepos"),
        ]
        session.add_all(payment_methods)
        await session.flush()

        # 6. Coupons & Promotions
        session.add(Coupon(code="WELCOME10", discount_type=DiscountType.PERCENTAGE, discount_value=10, expiry_date=date.today() + timedelta(days=90), is_active=True))
        session.add(Promotion(name="10% off Orders > ₹1000", promotion_scope=PromotionScope.ORDER, minimum_order_amount=1000, discount_type=PromotionDiscountType.PERCENTAGE, discount_value=10, is_active=True))
        await session.flush()

        # 7. POS Sessions & Historical Orders
        now = datetime.now(timezone.utc)
        
        # Create a closed session from yesterday
        yesterday_session = PosSession(
            opened_by=users[2].id,
            opened_at=now - timedelta(days=1, hours=10),
            closed_at=now - timedelta(days=1, hours=2),
            opening_balance=1000,
            closing_balance=5000,
            status=SessionStatus.CLOSED
        )
        # Create an open session for today
        today_session = PosSession(
            opened_by=users[2].id,
            opened_at=now - timedelta(hours=4),
            opening_balance=1000,
            status=SessionStatus.OPEN
        )
        session.add_all([yesterday_session, today_session])
        await session.flush()

        # Generate 150 Orders (100 past, 50 active)
        print("Generating 150 Orders (Items & Payments)...")
        orders = []
        for i in range(150):
            is_past = i < 100
            order_session = yesterday_session if is_past else today_session
            order_time = (now - timedelta(days=1, hours=random.randint(3, 9))) if is_past else (now - timedelta(minutes=random.randint(5, 200)))
            status = OrderStatus.PAID if is_past else random.choice([OrderStatus.DRAFT, OrderStatus.SENT_TO_KITCHEN, OrderStatus.PREPARING, OrderStatus.READY, OrderStatus.PAID])
            
            o = Order(
                order_number=f"ORD-{order_session.id}-{i+1000}",
                session_id=order_session.id,
                table_id=random.choice(tables).id if random.random() > 0.3 else None,
                customer_id=random.choice(customers).id if random.random() > 0.5 else None,
                employee_id=users[2].id,
                order_type=OrderType.DINE_IN if random.random() > 0.3 else OrderType.TAKEAWAY,
                status=status,
                subtotal=0, tax_amount=0, discount_amount=0, total_amount=0,
                created_at=order_time,
                updated_at=order_time
            )
            session.add(o)
            await session.flush()
            orders.append(o)

            # Add Order Items
            subtotal = 0
            tax_total = 0
            for _ in range(random.randint(1, 6)):
                p = random.choice(products)
                qty = random.randint(1, 3)
                line_total = p.price * qty
                tax = line_total * (p.tax_percentage / 100)
                subtotal += line_total
                tax_total += tax
                
                k_status = KitchenStatus.COMPLETED if is_past else random.choice(list(KitchenStatus))
                
                session.add(OrderItem(
                    order_id=o.id,
                    product_id=p.id,
                    quantity=qty,
                    unit_price=p.price,
                    tax_amount=tax,
                    discount_amount=0,
                    line_total=line_total,
                    kitchen_status=k_status
                ))
            
            o.subtotal = subtotal
            o.tax_amount = tax_total
            o.total_amount = subtotal + tax_total

            if o.status == OrderStatus.PAID:
                pm = random.choice(payment_methods)
                session.add(Payment(
                    order_id=o.id,
                    payment_method_id=pm.id,
                    amount=o.total_amount,
                    status=PaymentStatus.SUCCESS,
                    paid_at=order_time + timedelta(minutes=random.randint(5, 45)),
                    created_at=order_time + timedelta(minutes=random.randint(5, 45))
                ))

        await session.flush()

        # 8. Reservations
        print("Generating Reservations...")
        for i in range(20):
            res_date = (now + timedelta(days=random.randint(-5, 10))).date()
            session.add(Reservation(
                customer_name=random.choice(customers).name,
                customer_email=f"res{i}@example.com",
                customer_phone=f"99{random.randint(10000000, 99999999)}",
                table_id=random.choice(tables).id,
                reservation_date=res_date,
                start_time=(now + timedelta(hours=random.randint(1, 8))).time(),
                end_time=(now + timedelta(hours=random.randint(9, 11))).time(),
                guest_count=random.randint(2, 8),
                status=random.choice(list(ReservationStatus)),
                source=random.choice(list(ReservationSource)),
            ))

        await session.commit()
        print("Massive Demo Data Seeding Completed!")
        print("   -> 5 Users")
        print("   -> 50 Customers")
        print("   -> 3 Floors, ~35 Tables")
        print("   -> 6 Categories, ~50 Products")
        print("   -> 2 POS Sessions")
        print("   -> 150 Orders (100 Paid Historical, 50 Active)")
        print("   -> 20 Reservations")


if __name__ == "__main__":
    asyncio.run(seed_massive_data())
