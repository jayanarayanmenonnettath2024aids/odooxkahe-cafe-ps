"""
End-to-End Judge Flow Test (Section 25).
Runs the entire core business flow expected by judges.
"""

import asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.database import Base, get_db

test_engine = create_async_engine('sqlite+aiosqlite:///./judge_flow.db', echo=False)
test_session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with test_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

app.dependency_overrides[get_db] = override_get_db

async def setup():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)



async def run_judge_flow():
    await setup()
    print("Starting Judge Flow Test (Section 25)...")
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 0: Ensure Admin User Exists
        print("  - Creating Admin User (if not exists)...")
        await client.post("/auth/signup", json={
            "name": "Judge Admin",
            "email": "judge@admin.com",
            "password": "judgepassword",
            "role": "ADMIN"
        })

        # Step 1: Admin Login
        print("  - Admin Login...")
        res = await client.post("/auth/login", json={
            "email": "judge@admin.com",
            "password": "judgepassword"
        })
        assert res.status_code == 200, "Login failed"
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("    Success")

        # Step 2: Create Category
        print("  - Create Category...")
        res = await client.post("/categories", json={
            "name": "Judge Specials",
            "color": "#FFD700"
        }, headers=headers)
        assert res.status_code == 200, f"Create category failed: {res.json()}"
        cat_id = res.json()["data"]["id"]
        print("    Success")

        # Step 3: Create Product
        print("  - Create Product...")
        res = await client.post("/products", json={
            "name": "Hackathon Coffee",
            "description": "Brewed with tears and logic",
            "price": 500,
            "tax_percentage": 10,
            "category_id": cat_id
        }, headers=headers)
        assert res.status_code == 200, f"Create product failed: {res.json()}"
        prod_id = res.json()["data"]["id"]
        print("    Success")

        # Step 4: Create Floor
        print("  - Create Floor...")
        res = await client.post("/floors", json={
            "name": "Main Stage"
        }, headers=headers)
        assert res.status_code == 200, f"Create floor failed: {res.json()}"
        floor_id = res.json()["data"]["id"]
        print("    Success")

        # Step 5: Create Table
        print("  - Create Table...")
        res = await client.post("/tables", json={
            "floor_id": floor_id,
            "table_number": "JudgeTable",
            "seat_count": 4
        }, headers=headers)
        assert res.status_code == 200, f"Create table failed: {res.json()}"
        table_id = res.json()["data"]["id"]
        print("    Success")

        # Create Coupon for later
        res = await client.post("/coupons", json={
            "code": "HACK100",
            "discount_type": "FIXED",
            "discount_value": 100,
            "expiry_date": "2030-12-31"
        }, headers=headers)
        coupon_id = res.json()["data"]["id"]

        # Step 6: Open Session
        print("  - Open POS Session...")
        res = await client.post("/pos/session/open", json={
            "opening_balance": 1000
        }, headers=headers)
        assert res.status_code == 200, f"Open session failed: {res.json()}"
        session_id = res.json()["data"]["id"]
        print("    Success")

        # Step 7: Select Table & Create Order (POS creates order for table)
        print("  - Create Order for Table...")
        res = await client.post("/pos/select-table", json={
            "table_id": table_id,
            "session_id": session_id
        }, headers=headers)
        assert res.status_code == 200, f"Select table failed: {res.json()}"
        order_id = res.json()["data"]["current_order"]["id"]
        print("    Success")

        # Step 8: Add Products
        print("  - Add Products to Order...")
        res = await client.post("/pos/cart/add-product", json={
            "order_id": order_id,
            "product_id": prod_id,
            "quantity": 2
        }, headers=headers)
        assert res.status_code == 200, f"Add product failed: {res.json()}"
        print("    Success")

        # Step 9: Apply Coupon
        print("  - Apply Coupon...")
        res = await client.post("/pos/order/apply-coupon", json={
            "order_id": order_id,
            "coupon_code": "HACK100"
        }, headers=headers)
        assert res.status_code == 200, f"Apply coupon failed: {res.json()}"
        print("    Success")

        # Step 10: Send To Kitchen
        print("  - Send Order To Kitchen...")
        res = await client.post("/pos/order/send-to-kitchen", json={
            "order_id": order_id
        }, headers=headers)
        assert res.status_code == 200, f"Send to kitchen failed: {res.json()}"
        print("    Success")

        # Step 11: KDS Receives Order & Move To Preparing
        print("  - KDS Move To Preparing...")
        res = await client.patch(f"/kds/order/{order_id}/next-stage", headers=headers)
        assert res.status_code == 200, f"KDS preparing failed: {res.json()}"
        print("    Success")

        # Step 12: Move To Completed
        print("  - KDS Move To Ready/Completed...")
        res = await client.patch(f"/kds/order/{order_id}/next-stage", headers=headers)
        assert res.status_code == 200, f"KDS ready failed: {res.json()}"
        print("    Success")

        # Create Cash Payment Method
        res = await client.post("/payment-methods", json={
            "name": "CASH",
            "type": "CASH"
        }, headers=headers)
        assert res.status_code == 200, f"Create payment method failed: {res.json()}"

        # Step 13: Pay Using Cash
        print("  - Pay Using Cash...")
        # Get order details to know exact total
        res = await client.get(f"/pos/order-summary/{order_id}", headers=headers)
        order_total = res.json()["data"]["total_amount"]
        
        res = await client.post("/payment/cash", json={
            "order_id": order_id,
            "received_amount": order_total
        }, headers=headers)
        assert res.status_code == 200, f"Payment failed: {res.json()}"
        print("    Success")

        # Step 14: Order Marked Paid
        res = await client.get(f"/pos/order-summary/{order_id}", headers=headers)
        assert res.json()["data"]["status"] == "PAID", "Order is not marked PAID"
        print("  - Order correctly marked PAID")

        # Step 15: Session Closed
        print("  - Close POS Session...")
        res = await client.post("/pos/session/close", json={
            "session_id": session_id
        }, headers=headers)
        assert res.status_code == 200, f"Close session failed: {res.json()}"
        print("    Success")

        # Step 16: Report Shows Sale
        print("  - Verify Report Shows Sale...")
        res = await client.get("/reports/dashboard?date_filter=today", headers=headers)
        assert res.status_code == 200, f"Dashboard failed: {res.json()}"
        data = res.json()["data"]
        assert data["total_orders"] >= 1, "Dashboard does not show the order"
        print("    Success")

        print("END-TO-END JUDGE FLOW PASSED! SUCCESS!")


if __name__ == "__main__":
    asyncio.run(run_judge_flow())
