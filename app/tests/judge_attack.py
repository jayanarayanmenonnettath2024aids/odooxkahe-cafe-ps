import asyncio
import json
import os
import traceback
from colorama import init, Fore
import httpx
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:runtime@localhost:5432/postgres"

from app.main import app
from app.core.database import engine, Base
from app.seed import seed_db

init(autoreset=True)

class AttackRunner:
    def __init__(self):
        self.results = []
        self.client = None
        self.admin_headers = {}
        self.emp_headers = {}
        self.BASE_URL = "http://test"

    def record(self, attack_name, endpoint, payload, response_status, response_body, severity, defended, details=""):
        res = {
            "attack": attack_name,
            "endpoint": endpoint,
            "payload": payload,
            "status": response_status,
            "response": response_body,
            "severity": severity,
            "defended": defended,
            "details": details
        }
        self.results.append(res)
        color = Fore.GREEN if defended else Fore.RED
        print(color + f"[{'DEFENDED' if defended else 'VULNERABLE'}] {attack_name}")

    async def setup_state(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await seed_db()

        # Login admin
        res = await self.client.post("/auth/login", json={"email": "admin@cafepos.com", "password": "admin123"})
        self.admin_headers = {"Authorization": f"Bearer {res.json()['access_token']}"}

        # Create emp
        await self.client.post("/employees", json={"name": "Attacker", "email": "atk@x.com", "password": "password"}, headers=self.admin_headers)
        res_emp = await self.client.post("/auth/login", json={"email": "atk@x.com", "password": "password"})
        self.emp_headers = {"Authorization": f"Bearer {res_emp.json()['access_token']}"}

    async def run(self):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=self.BASE_URL) as client:
            self.client = client
            await self.setup_state()

            # Create base entities for attacks
            prod_res = await self.client.post("/products", json={"name": "Target", "price": 100, "category_id": 1, "is_active": True}, headers=self.admin_headers)
            prod_id = prod_res.json()["data"]["id"]

            table_res = await self.client.post("/tables", json={"floor_id": 1, "table_number": "ATK1", "seat_count": 2}, headers=self.admin_headers)
            table_id = table_res.json()["data"]["id"]
            
            coup_res = await self.client.post("/coupons", json={"code": "ATTACK50", "discount_type": "PERCENTAGE", "discount_value": 50, "valid_until": "2030-01-01T00:00:00Z"}, headers=self.admin_headers)
            
            # --- 1. Double Sessions ---
            sess1 = await self.client.post("/pos/session/open", json={"opening_balance": 100}, headers=self.emp_headers)
            sess1_id = sess1.json()["data"]["id"]
            
            sess2 = await self.client.post("/pos/session/open", json={"opening_balance": 100}, headers=self.emp_headers)
            defended = sess2.status_code != 200
            self.record("Double Sessions", "/pos/session/open", {"opening_balance": 100}, sess2.status_code, sess2.text, "Major", defended)

            # --- 2. Double Table Occupancy ---
            ord1 = await self.client.post("/pos/select-table", json={"table_id": table_id, "session_id": sess1_id}, headers=self.emp_headers)
            ord1_id = ord1.json()["data"]["current_order"]["id"]
            
            ord2 = await self.client.post("/pos/select-table", json={"table_id": table_id, "session_id": sess1_id}, headers=self.emp_headers)
            # Depending on business logic, selecting an occupied table either returns the same order, or denies it.
            # If it creates a NEW order (different ID) for the same occupied table, it's a vulnerability.
            ord2_id = ord2.json().get("data", {}).get("current_order", {}).get("id")
            defended_table = ord2.status_code != 200 or ord1_id == ord2_id
            self.record("Double Table Occupancy", "/pos/select-table", {"table_id": table_id}, ord2.status_code, ord2.text, "Critical", defended_table)

            # Populate order
            await self.client.post("/pos/cart/add-product", json={"order_id": ord1_id, "product_id": prod_id, "quantity": 1}, headers=self.emp_headers)

            # --- 3. Session close with unpaid orders ---
            close_sess = await self.client.post("/pos/session/close", json={"session_id": sess1_id, "closing_balance": 100}, headers=self.emp_headers)
            defended_close = close_sess.status_code != 200
            self.record("Close Session With Unpaid Orders", "/pos/session/close", {"session_id": sess1_id}, close_sess.status_code, close_sess.text, "Major", defended_close)

            # --- 4. Double Payments ---
            # Transition to SENT_TO_KITCHEN so payment is accepted
            await self.client.post(f"/pos/order/{ord1_id}/send-to-kitchen", headers=self.emp_headers)

            pay1 = await self.client.post("/payment/cash", json={"order_id": ord1_id, "received_amount": 200}, headers=self.emp_headers)
            pay2 = await self.client.post("/payment/cash", json={"order_id": ord1_id, "received_amount": 200}, headers=self.emp_headers)
            defended_pay = pay2.status_code != 200
            self.record("Double Payments", "/payment/cash", {"order_id": ord1_id, "received_amount": 200}, pay2.status_code, pay2.text, "Critical", defended_pay)

            # --- 5. Concurrent Order Modifications (Modify PAID order) ---
            mod = await self.client.post("/pos/cart/add-product", json={"order_id": ord1_id, "product_id": prod_id, "quantity": 1}, headers=self.emp_headers)
            defended_mod = mod.status_code != 200
            self.record("Modify PAID Order", "/pos/cart/add-product", {"order_id": ord1_id}, mod.status_code, mod.text, "Critical", defended_mod)

            # --- 6. Delete Product Used in Active Order ---
            sess3_id = sess1_id
            
            ord3 = await self.client.post("/pos/select-table", json={"table_id": 1, "session_id": sess3_id}, headers=self.emp_headers)
            ord3_id = ord3.json()["data"]["current_order"]["id"]
            await self.client.post("/pos/cart/add-product", json={"order_id": ord3_id, "product_id": prod_id, "quantity": 1}, headers=self.emp_headers)
            
            del_prod = await self.client.delete(f"/products/{prod_id}", headers=self.admin_headers)
            # The IntegrityError handler should catch this and return 400
            defended_del = del_prod.status_code in [400, 409]
            self.record("Delete Active Product", f"/products/{prod_id}", {}, del_prod.status_code, del_prod.text, "Major", defended_del)

            # --- 7. Delete Table With Active Order ---
            del_table = await self.client.delete(f"/tables/1", headers=self.admin_headers)
            defended_delt = del_table.status_code in [400, 409]
            self.record("Delete Active Table", f"/tables/1", {}, del_table.status_code, del_table.text, "Major", defended_delt)

            # --- 8. Payment Replay Attack ---
            pay_upi1 = await self.client.post("/payment/upi", json={"order_id": ord3_id}, headers=self.emp_headers)
            payment_id = pay_upi1.json().get("data", {}).get("payment_id", 1)
            # Simulate confirming the same transaction ID on two orders
            # But wait, ord3 has a balance of 100.
            conf1 = await self.client.post("/payment/upi/confirm", json={"payment_id": payment_id, "transaction_reference": "TXN_REPLAY"}, headers=self.emp_headers)
            
            # Create ord4 to replay the same TXN
            ord4 = await self.client.post("/pos/select-table", json={"table_id": table_id, "session_id": sess3_id}, headers=self.emp_headers)
            ord4_id = ord4.json()["data"]["current_order"]["id"]
            pay_upi2 = await self.client.post("/payment/upi", json={"order_id": ord4_id}, headers=self.emp_headers)
            payment_id2 = pay_upi2.json().get("data", {}).get("payment_id", 2)
            conf2 = await self.client.post("/payment/upi/confirm", json={"payment_id": payment_id2, "transaction_reference": "TXN_REPLAY"}, headers=self.emp_headers)
            
            defended_replay = conf2.status_code != 200
            self.record("Payment Replay Attack", "/payment/upi/confirm", {"transaction_reference": "TXN_REPLAY"}, conf2.status_code, conf2.text, "Critical", defended_replay)

            # --- 9. Invalid QR Tokens ---
            qr = await self.client.get("/s/FAKE_TOKEN")
            defended_qr = qr.status_code == 404
            self.record("Invalid QR Token", "/s/FAKE_TOKEN", {}, qr.status_code, qr.text, "Minor", defended_qr)

            # --- 10. Order State Transition Abuse ---
            # Try to complete an order that wasn't prepared
            state = await self.client.put(f"/kds/order/{ord4_id}/status", json={"status": "COMPLETED"}, headers=self.emp_headers)
            defended_state = state.status_code != 200
            self.record("State Transition Abuse", f"/kds/order/{ord4_id}/status", {"status": "COMPLETED"}, state.status_code, state.text, "Major", defended_state)

            # Write to file
            with open("attack_results.json", "w") as f:
                json.dump(self.results, f, indent=2)

if __name__ == "__main__":
    runner = AttackRunner()
    asyncio.run(runner.run())
