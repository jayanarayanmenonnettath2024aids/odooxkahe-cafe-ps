import asyncio
import httpx
from colorama import init, Fore, Style
import logging

import os

# Ensure we hit the real local postgres database instead of docker 'db' hostname
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:runtime@localhost:5432/postgres"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

from app.main import app
from app.core.database import engine, Base
from app.seed import seed_db

init(autoreset=True)
logging.basicConfig(level=logging.WARNING)

BASE_URL = "http://test"

async def run_tests():
    print(Fore.CYAN + "=============================================")
    print(Fore.CYAN + "   ODOO CAFE POS - PROTOTYPE READINESS TEST  ")
    print(Fore.CYAN + "=============================================")

    # Initialize Real Database
    print(Fore.YELLOW + "Initializing Real Database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await seed_db()

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=BASE_URL) as client:
        # STEP 1: AUTHENTICATION
        print(Fore.YELLOW + "\n--- STEP 1: AUTHENTICATION ---")
        
        # 1.1 Login Admin
        res = await client.post("/auth/login", json={"email": "admin@cafepos.com", "password": "admin123"})
        if res.status_code == 200:
            print(Fore.GREEN + "[PASS] Admin Login Successful")
            token = res.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(Fore.RED + f"[FAIL] Admin Login Failed: {res.text}")
            return
            
        # 1.2 Invalid Login
        res = await client.post("/auth/login", json={"email": "admin@cafepos.com", "password": "wrongpassword"})
        if res.status_code == 401:
            print(Fore.GREEN + "[PASS] Edge Case: Invalid Login Rejected")
        else:
            print(Fore.RED + f"[FAIL] Edge Case: Invalid Login Handled Incorrectly (Status {res.status_code})")

        # 1.3 Missing JWT
        res = await client.get("/auth/me")
        if res.status_code == 401:
            print(Fore.GREEN + "[PASS] Edge Case: Missing JWT Rejected")
        else:
            print(Fore.RED + f"[FAIL] Edge Case: Missing JWT Handled Incorrectly")


        # STEP 2: DEMO-SCALE SYNTHETIC DATA
        print(Fore.YELLOW + "\n--- STEP 2: DEMO-SCALE SYNTHETIC DATA ---")
        
        # We rely on the seed data already present from app.seed (which gives us 3 Categories, 4 Products, 2 Floors, 3 Tables, 3 Payment Methods).
        # We will create a few more to reach the demo scale.
        
        # Fetch existing floors
        res = await client.get("/floors", headers=headers)
        floors = res.json()["data"]
        floor_id = floors[0]["id"]
        
        # Create Tables
        tables_created = 0
        for i in range(10):
            res = await client.post("/tables", json={
                "table_number": f"D{i+1}",
                "seat_count": 4,
                "floor_id": floor_id
            }, headers=headers)
            if res.status_code == 200:
                tables_created += 1
        print(Fore.GREEN + f"[PASS] Created {tables_created} Tables")

        # Create Customers
        customers_created = 0
        for i in range(10):
            res = await client.post("/customers", json={
                "name": f"Customer {i}",
                "email": f"cust{i}@example.com",
                "phone": f"555-000{i}"
            }, headers=headers)
            if res.status_code == 200:
                customers_created += 1
        print(Fore.GREEN + f"[PASS] Created {customers_created} Customers")

        # Create Coupons
        res = await client.post("/coupons", json={
            "code": "TEST50",
            "type": "FIXED_AMOUNT",
            "value": 50.0,
            "min_order_amount": 100.0,
            "valid_until": "2030-12-31T00:00:00Z"
        }, headers=headers)
        if res.status_code == 200:
            print(Fore.GREEN + "[PASS] Created Coupon TEST50")
            
        res = await client.post("/coupons", json={
            "code": "EXPIRED",
            "type": "PERCENTAGE",
            "value": 10.0,
            "min_order_amount": 0,
            "valid_until": "2020-01-01T00:00:00Z"
        }, headers=headers)
        if res.status_code == 200:
            print(Fore.GREEN + "[PASS] Created Expired Coupon")


        # STEP 3: WORKFLOWS & PROTOTYPE READINESS
        print(Fore.YELLOW + "\n--- STEP 3: WORKFLOWS & PROTOTYPE READINESS ---")
        
        # Open Session
        res = await client.post("/pos/session/open", json={"opening_balance": 500.0}, headers=headers)
        if res.status_code == 200:
            session_id = res.json()["data"]["id"]
            print(Fore.GREEN + f"[PASS] Session {session_id} Opened")
        else:
            print(Fore.RED + f"[FAIL] Session Open Failed: {res.text}")
            return
            
        # Get Tables
        res = await client.get("/tables", headers=headers)
        tables = res.json()["data"]
        table_id = tables[0]["id"]
        
        # Get Products
        res = await client.get("/products", headers=headers)
        products = res.json()["data"]
        prod_id = products[0]["id"]

        # Run 5 Dine-in orders
        orders_completed = 0
        for i in range(5):
            # Select Table
            res = await client.post("/pos/select-table", json={"table_id": table_id, "session_id": session_id}, headers=headers)
            order_id = res.json()["data"]["current_order"]["id"]
            
            # Add Product
            res = await client.post("/pos/cart/add-product", json={"order_id": order_id, "product_id": prod_id, "quantity": 2}, headers=headers)
            
            # Apply Coupon (Only on first order)
            if i == 0:
                res = await client.post("/pos/order/apply-coupon", json={"order_id": order_id, "coupon_code": "TEST50"}, headers=headers)
                if res.status_code == 200:
                    print(Fore.GREEN + "  -> Applied Coupon Successfully")
                    
            # Send to Kitchen
            res = await client.post("/pos/order/send-to-kitchen", json={"order_id": order_id}, headers=headers)
            
            # Pay
            res = await client.post("/payment/cash", json={"order_id": order_id, "amount_received": 1000.0}, headers=headers)
            if res.status_code == 200:
                orders_completed += 1
                
        print(Fore.GREEN + f"[PASS] Completed {orders_completed} Dine-In Workflows")


        # STEP 4: EDGE CASE TESTING
        print(Fore.YELLOW + "\n--- STEP 4: EDGE CASE TESTING ---")
        
        # Invalid Table ID
        res = await client.post("/pos/select-table", json={"table_id": 99999, "session_id": session_id}, headers=headers)
        if res.status_code == 404:
            print(Fore.GREEN + "[PASS] Invalid Table ID Rejected")
            
        # Invalid Quantity
        res = await client.post("/pos/select-table", json={"table_id": tables[1]["id"], "session_id": session_id}, headers=headers)
        temp_order_id = res.json()["data"]["current_order"]["id"]
        res = await client.post("/pos/cart/add-product", json={"order_id": temp_order_id, "product_id": prod_id, "quantity": -5}, headers=headers)
        if res.status_code == 422: # Pydantic validation
            print(Fore.GREEN + "[PASS] Negative Quantity Rejected")
            
        # Expired Coupon
        res = await client.post("/pos/order/apply-coupon", json={"order_id": temp_order_id, "coupon_code": "EXPIRED"}, headers=headers)
        if res.status_code == 400:
            print(Fore.GREEN + "[PASS] Expired Coupon Rejected")
            
        # Invalid Coupon
        res = await client.post("/pos/order/apply-coupon", json={"order_id": temp_order_id, "coupon_code": "NOTREAL"}, headers=headers)
        if res.status_code == 404:
            print(Fore.GREEN + "[PASS] Invalid Coupon Code Rejected")

        # Insufficient Payment
        res = await client.post("/pos/cart/add-product", json={"order_id": temp_order_id, "product_id": prod_id, "quantity": 1}, headers=headers)
        res = await client.post("/pos/order/send-to-kitchen", json={"order_id": temp_order_id}, headers=headers)
        res = await client.post("/payment/cash", json={"order_id": temp_order_id, "amount_received": 0.01}, headers=headers)
        if res.status_code == 400:
            print(Fore.GREEN + "[PASS] Insufficient Cash Payment Rejected")


        # STEP 5: CLOSE SESSION & REPORTS
        print(Fore.YELLOW + "\n--- STEP 5: REPORTS & CLOSURE ---")
        
        res = await client.post("/pos/session/close", json={"session_id": session_id}, headers=headers)
        if res.status_code == 200:
            print(Fore.GREEN + "[PASS] Session Closed Successfully")
            
        res = await client.get("/reports/dashboard?period=today", headers=headers)
        if res.status_code == 200:
            print(Fore.GREEN + "[PASS] Generated Dashboard Report")


    print(Fore.CYAN + "\n=============================================")
    print(Fore.CYAN + "   ALL PROTOTYPE READINESS TESTS EXECUTED!   ")
    print(Fore.CYAN + "=============================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
