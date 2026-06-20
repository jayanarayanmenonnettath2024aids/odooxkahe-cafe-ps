import asyncio
import json
import os
import traceback
from datetime import datetime
from pprint import pformat
from colorama import init, Fore, Style
import httpx
from fastapi.testclient import TestClient

# Must be set before importing app modules
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:runtime@localhost:5432/postgres"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

from app.main import app
from app.core.database import engine, Base
from app.seed import seed_db

init(autoreset=True)

class MasterQA_Suite:
    def __init__(self):
        self.stats = {
            "Total Executed": 0,
            "Passed": 0,
            "Failed": 0,
            "Critical Bugs": 0,
            "Major Bugs": 0,
            "Minor Bugs": 0,
            "Missing Features": 0,
            "Security Issues": 0,
            "Data Integrity Issues": 0,
            "Websocket Issues": 0,
        }
        self.fails = []
        self.client = None
        self.ws_client = TestClient(app)
        self.admin_token = None
        self.emp_token = None
        self.admin_headers = {}
        self.emp_headers = {}
        self.BASE_URL = "http://test"

    def log_pass(self, phase, message):
        self.stats["Total Executed"] += 1
        self.stats["Passed"] += 1
        print(Fore.GREEN + f"[PASS] {phase}: {message}")

    def log_fail(self, phase, message, bug_type="Major Bugs", payload=None, error=None):
        self.stats["Total Executed"] += 1
        self.stats["Failed"] += 1
        self.stats[bug_type] += 1
        print(Fore.RED + f"[FAIL] {phase}: {message}")
        
        fail_record = {
            "phase": phase,
            "message": message,
            "bug_type": bug_type
        }
        if payload:
            print(Fore.YELLOW + "  Payload/Response: " + str(payload)[:500])
            fail_record["payload"] = payload
        if error:
            print(Fore.YELLOW + "  Error: " + str(error))
            fail_record["error"] = str(error)
            
        self.fails.append(fail_record)

    async def execute_phase(self, phase_num, name, coro):
        print(Fore.CYAN + f"\n=== PHASE {phase_num}: {name} ===")
        try:
            await coro()
        except Exception as e:
            self.log_fail(f"PHASE {phase_num}", "Unhandled Exception crashed the phase", "Critical Bugs", error=traceback.format_exc())

    async def p1_system_health(self):
        try:
            print("Resetting database...")
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            await seed_db()
            self.log_pass("P1", "Database dropped and re-seeded successfully.")
        except Exception as e:
            self.log_fail("P1", "System Boot / DB Migration failed", "Critical Bugs", error=str(e))

    async def p2_data_model(self):
        # Attempt an invalid constraint insert (e.g. invalid foreign key for table)
        res = await self.client.post("/tables", json={"floor_id": 9999, "table_number": "T99", "seat_count": 2}, headers=self.admin_headers)
        if res.status_code in [404, 422, 400]:
            self.log_pass("P2", "Invalid FK insertion properly rejected")
        else:
            self.log_fail("P2", "Invalid FK insertion was not properly handled", "Data Integrity Issues", payload=res.json())

    async def p3_role_matrix(self):
        # Admin setup
        res = await self.client.post("/auth/login", json={"email": "admin@cafepos.com", "password": "admin123"})
        if res.status_code == 200:
            self.admin_token = res.json()["access_token"]
            self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            self.log_pass("P3", "Admin authentication successful")
        else:
            self.log_fail("P3", "Admin auth failed", "Critical Bugs", payload=res.text)
            
        # Employee Setup
        emp_res = await self.client.post("/employees", json={"name": "Emp 1", "email": "emp1@cafepos.com", "password": "password"}, headers=self.admin_headers)
        if emp_res.status_code in [200, 201]:
            self.log_pass("P3", "Employee created by Admin")
            emp_login = await self.client.post("/auth/login", json={"email": "emp1@cafepos.com", "password": "password"})
            self.emp_token = emp_login.json()["access_token"]
            self.emp_headers = {"Authorization": f"Bearer {self.emp_token}"}
        else:
            self.log_fail("P3", "Employee creation failed", "Major Bugs", payload=emp_res.text)

        # Role Verification - Employee accessing Admin endpoint
        res_unauth = await self.client.post("/employees", json={"name": "Hacker", "email": "hacker@x.com", "password": "pw"}, headers=self.emp_headers)
        if res_unauth.status_code in [401, 403]:
            self.log_pass("P3", "Employee strictly prevented from Admin route")
        else:
            self.log_fail("P3", "Employee accessed Admin route", "Security Issues", payload=res_unauth.status_code)

    async def p4_product_lifecycle(self):
        cat_res = await self.client.post("/categories", json={"name": "Test Cat", "color": "#000"}, headers=self.admin_headers)
        if cat_res.status_code == 200:
            cat_id = cat_res.json()["data"]["id"]
            self.log_pass("P4", "Category created")
            
            prod_res = await self.client.post("/products", json={"name": "Test Prod", "price": 10.0, "category_id": cat_id, "is_active": True}, headers=self.admin_headers)
            if prod_res.status_code == 200:
                prod_id = prod_res.json()["data"]["id"]
                self.log_pass("P4", "Product created")
                
                upd_res = await self.client.put(f"/products/{prod_id}", json={"is_active": False}, headers=self.admin_headers)
                if upd_res.status_code == 200:
                    self.log_pass("P4", "Product disabled successfully")
                else:
                    self.log_fail("P4", "Product update failed", payload=upd_res.text)
            else:
                self.log_fail("P4", "Product creation failed", payload=prod_res.text)
        else:
            self.log_fail("P4", "Category creation failed", payload=cat_res.text)

    async def p5_table_lifecycle(self):
        res = await self.client.get("/tables/status", headers=self.admin_headers)
        if res.status_code == 200:
            self.log_pass("P5", "Table statuses retrieved")
        else:
            self.log_fail("P5", "Table status retrieval failed", payload=res.text)

    async def p6_qr_validation(self):
        # Missing feature explicit test
        res = await self.client.get("/tables/1/qr-pdf", headers=self.admin_headers)
        if res.status_code == 404:
            self.log_fail("P6", "QR PDF Export Endpoint Missing", "Missing Features")
        else:
            self.log_pass("P6", "QR PDF Export hit")

        res2 = await self.client.get("/tables/bulk-qr", headers=self.admin_headers)
        if res2.status_code == 404:
            self.log_fail("P6", "Bulk QR Endpoint Missing", "Missing Features")

    async def p7_session_mgmt(self):
        res = await self.client.post("/pos/session/open", json={"opening_balance": 100}, headers=self.emp_headers)
        if res.status_code == 200:
            self.session_id = res.json()["data"]["id"]
            self.log_pass("P7", "Session opened")
        else:
            self.session_id = None
            self.log_fail("P7", "Session opening failed", payload=res.text)

    async def p8_p9_coupons_promotions(self):
        res = await self.client.post("/coupons", json={"code": "MASTER20", "discount_type": "PERCENTAGE", "discount_value": 20, "valid_until": "2030-01-01T00:00:00Z"}, headers=self.admin_headers)
        if res.status_code == 200:
            self.log_pass("P8", "Coupon generated")
        else:
            self.log_fail("P8", "Coupon generation failed", payload=res.text)

        res_promo = await self.client.post("/promotions", json={"name": "Happy Hour", "promotion_type": "ORDER_DISCOUNT", "discount_type": "PERCENTAGE", "discount_value": 10, "is_active": True}, headers=self.admin_headers)
        if res_promo.status_code == 200:
            self.log_pass("P9", "Promotion generated")
        else:
            self.log_fail("P9", "Promotion generation failed", payload=res_promo.text)

    async def p10_to_p12_orders(self):
        if not self.session_id:
            self.log_fail("P10", "Skipped orders due to session failure", "Critical Bugs")
            return

        res = await self.client.post("/pos/select-table", json={"table_id": 1, "session_id": self.session_id}, headers=self.emp_headers)
        if res.status_code == 200:
            order_id = res.json()["data"]["current_order"]["id"]
            self.log_pass("P10", "Dine-In Order initialized")
            
            # Add item to cart before sending to kitchen
            add_res = await self.client.post("/pos/cart/add-product", json={"order_id": order_id, "product_id": 1, "quantity": 2}, headers=self.emp_headers)
            if add_res.status_code == 200:
                self.log_pass("P10", "Item added to cart")
            else:
                self.log_fail("P10", "Failed to add item to cart", payload=add_res.text)

            # Apply Coupon before KDS
            cp_res = await self.client.post("/pos/order/apply-coupon", json={"order_id": order_id, "coupon_code": "MASTER20"}, headers=self.emp_headers)
            if cp_res.status_code == 200:
                self.log_pass("P10", "Coupon applied to order")
            else:
                self.log_fail("P10", "Coupon apply failed", payload=cp_res.text)

            # Send to Kitchen
            kds_res = await self.client.post("/pos/order/send-to-kitchen", json={"order_id": order_id}, headers=self.emp_headers)
            if kds_res.status_code == 200:
                self.log_pass("P11", "Sent to KDS successfully")
            else:
                self.log_fail("P11", "KDS send failed", payload=kds_res.text)
                
            self.test_order_id = order_id
        else:
            self.log_fail("P10", "Order init failed", payload=res.text)

    async def p13_self_ordering(self):
        res = await self.client.get("/s/config", headers=self.emp_headers)
        if res.status_code == 404:
            self.log_fail("P13", "Self Ordering Config API Missing", "Missing Features")

    async def p14_payments(self):
        if hasattr(self, 'test_order_id'):
            res = await self.client.post("/payment/cash", json={"order_id": self.test_order_id, "received_amount": 9999.0}, headers=self.emp_headers)
            if res.status_code == 200:
                self.log_pass("P14", "Cash Payment Processed")
            else:
                self.log_fail("P14", "Payment Process Failed", payload=res.text)

    async def p15_receipts(self):
        if hasattr(self, 'test_order_id'):
            res = await self.client.get(f"/pos/receipt/{self.test_order_id}/pdf", headers=self.emp_headers)
            if res.status_code == 200:
                self.log_pass("P15", "PDF Receipt Generated")
            else:
                self.log_fail("P15", "PDF Receipt Generation Failed", "Missing Features", payload=res.text)

    async def p16_reporting(self):
        res = await self.client.get("/reports/export?format=xlsx", headers=self.admin_headers)
        if res.status_code == 404:
            self.log_fail("P16", "Excel Report Export Missing", "Missing Features")
        else:
            self.log_pass("P16", "Hit report export")

    async def p17_websockets(self):
        try:
            with self.ws_client.websocket_connect("/ws") as websocket:
                websocket.send_json({"type": "subscribe", "channel": "tables"})
                self.log_pass("P17", "Websocket connection & subscription succeeded")
        except Exception as e:
            self.log_fail("P17", "Websocket connection failed", "Websocket Issues", error=str(e))

    async def p18_failure_recovery(self):
        # We can't realistically restart the server in standard asyncio, but we can attempt malformed data
        res = await self.client.post("/pos/cart/add-product", json={"order_id": -999, "product_id": -1, "quantity": 1}, headers=self.emp_headers)
        if res.status_code in [404, 422]:
            self.log_pass("P18", "System safely rejects ghost orders gracefully")
        else:
            self.log_fail("P18", "Ghost order returned unexpected 500", "Data Integrity Issues")

    async def p19_accounting(self):
        res = await self.client.get("/reports/dashboard?period=today", headers=self.admin_headers)
        if res.status_code == 200:
            self.log_pass("P19", "Accounting retrieved for recalculation")
        else:
            self.log_fail("P19", "Dashboard accounting query failed", payload=res.text)

    async def p20_judge_demo(self):
        if hasattr(self, 'session_id') and self.session_id:
            res = await self.client.post("/pos/session/close", json={"session_id": self.session_id, "closing_balance": 100}, headers=self.emp_headers)
            if res.status_code == 200:
                self.log_pass("P20", "End of day session close successful")
            else:
                self.log_fail("P20", "Session closure failed", payload=res.text)

    async def run(self):
        print(Fore.YELLOW + "INITIALIZING MASTER QA RUNNER...")
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=self.BASE_URL) as client:
            self.client = client
            await self.execute_phase(1, "System Health & DB", self.p1_system_health)
            await self.execute_phase(3, "Role Permission Matrix", self.p3_role_matrix)
            await self.execute_phase(2, "Data Model Constraints", self.p2_data_model)
            await self.execute_phase(4, "Product Lifecycle", self.p4_product_lifecycle)
            await self.execute_phase(5, "Table Lifecycle", self.p5_table_lifecycle)
            await self.execute_phase(6, "QR Token Validation", self.p6_qr_validation)
            await self.execute_phase(7, "Session Management", self.p7_session_mgmt)
            await self.execute_phase("8/9", "Coupons & Promos", self.p8_p9_coupons_promotions)
            await self.execute_phase("10/11/12", "Orders & KDS", self.p10_to_p12_orders)
            await self.execute_phase(13, "Self Ordering", self.p13_self_ordering)
            await self.execute_phase(14, "Payments", self.p14_payments)
            await self.execute_phase(15, "Receipts", self.p15_receipts)
            await self.execute_phase(16, "Reporting Exports", self.p16_reporting)
            await self.execute_phase(17, "Websockets", self.p17_websockets)
            await self.execute_phase(18, "Failure Recovery", self.p18_failure_recovery)
            await self.execute_phase(19, "Accounting", self.p19_accounting)
            await self.execute_phase(20, "Complete Simulation End", self.p20_judge_demo)

        print("\n" + "="*50)
        print(" MASTER QA REPORT SUMMARY ")
        print("="*50)
        for k, v in self.stats.items():
            print(f"{k}: {v}")
            
        with open("master_test_results.json", "w") as f:
            json.dump({"stats": self.stats, "failures": self.fails}, f, indent=4)

if __name__ == "__main__":
    runner = MasterQA_Suite()
    asyncio.run(runner.run())
