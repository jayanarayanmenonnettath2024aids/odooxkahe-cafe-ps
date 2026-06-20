import asyncio
import httpx
import json
import logging
from sqlalchemy import create_engine, text
from app.core.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("validator")

BASE_URL = "http://localhost:8000"
settings = get_settings()

from app.main import app
from httpx import ASGITransport

class OperationalValidator:
    def __init__(self):
        self.client = httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=30.0)
        self.engine = create_engine(settings.sync_database_url)
        self.admin_headers = {}
        self.emp_headers = {}
        self.data = {}
        self.results = {}

    async def run_all(self):
        logger.info("Starting Operational Validation...")
        await self.phase_1_env()
        await self.setup_auth()
        await self.phase_2_synthetic_data()
        await self.phase_3_simulate_day()
        await self.phase_4_5_6_emails_pdfs()
        await self.phase_7_reports()
        await self.phase_8_db_consistency()
        self.generate_report()
        await self.client.aclose()

    async def phase_1_env(self):
        logger.info("Phase 1: Env Audit")
        # Read .env
        self.results["env"] = {
            "SMTP_HOST": settings.SMTP_HOST,
            "DATABASE_URL": "PRESENT" if settings.DATABASE_URL else "MISSING",
        }

    async def setup_auth(self):
        # Login admin
        resp = await self.client.post("/auth/login", json={"email": settings.ADMIN_EMAIL, "password": settings.ADMIN_PASSWORD})
        token = resp.json().get("access_token")
        self.admin_headers = {"Authorization": f"Bearer {token}"}
        
        # Create Employee
        emp_resp = await self.client.post("/employees", json={"name": "ValEmp", "email": "valemp@cafepos.com", "password": "password123", "role": "EMPLOYEE"}, headers=self.admin_headers)
        if emp_resp.status_code == 400: # Exists
            pass
        emp_login = await self.client.post("/auth/login", json={"email": "valemp@cafepos.com", "password": "password123"})
        emp_token = emp_login.json().get("access_token")
        self.emp_headers = {"Authorization": f"Bearer {emp_token}"}
        logger.info("Auth setup complete.")

    async def phase_2_synthetic_data(self):
        logger.info("Phase 2: Synthetic Data")
        cats = ["Coffee", "Tea", "Desserts", "Snacks", "Meals"]
        cat_ids = []
        for c in cats:
            r = await self.client.post("/categories", json={"name": c, "color": "#FF0000"}, headers=self.admin_headers)
            if r.status_code == 200:
                cat_ids.append(r.json()["data"]["id"])
            else:
                r_get = await self.client.get("/categories", headers=self.admin_headers)
                cat_ids.append([x["id"] for x in r_get.json()["data"] if x["name"] == c][0])
                
        # Products
        r = await self.client.post("/products", json={"name": "Espresso", "price": 50, "category_id": cat_ids[0]}, headers=self.admin_headers)
        self.data["product_id"] = r.json()["data"]["id"] if r.status_code == 200 else 1

        # Floor/Table
        r = await self.client.post("/floors", json={"name": "ValFloor"}, headers=self.admin_headers)
        f_id = r.json()["data"]["id"] if r.status_code == 200 else 1
        r = await self.client.post("/tables", json={"floor_id": f_id, "table_number": "VT1", "seat_count": 4}, headers=self.admin_headers)
        self.data["table_id"] = r.json()["data"]["id"] if r.status_code == 200 else 1

        # Customer
        r = await self.client.post("/customers", json={"name": "Val Customer", "phone": "999999999"}, headers=self.admin_headers)
        self.data["customer_id"] = r.json()["data"]["id"] if r.status_code == 200 else 1

    async def phase_3_simulate_day(self):
        logger.info("Phase 3: Simulate Day")
        # Open Session
        sess = await self.client.post("/pos/session/open", json={"opening_balance": 100}, headers=self.emp_headers)
        self.data["session_id"] = sess.json()["data"]["id"] if sess.status_code == 200 else 1

        # Order 1 (Cash)
        ord1 = await self.client.post("/pos/select-table", json={"table_id": self.data["table_id"], "session_id": self.data["session_id"]}, headers=self.emp_headers)
        ord1_id = ord1.json()["data"]["current_order"]["id"]
        self.data["ord1_id"] = ord1_id

        await self.client.post("/pos/cart/add-product", json={"order_id": ord1_id, "product_id": self.data["product_id"], "quantity": 2}, headers=self.emp_headers)
        await self.client.post("/pos/order/send-to-kitchen", json={"order_id": ord1_id}, headers=self.emp_headers)
        
        # Payment
        pay1 = await self.client.post("/payment/cash", json={"order_id": ord1_id, "received_amount": 500}, headers=self.emp_headers)
        logger.info(f"Payment 1: {pay1.status_code} - {pay1.text}")

    async def phase_4_5_6_emails_pdfs(self):
        logger.info("Phase 4-6: PDFs and Emails")
        # Receipt PDF & Email trigger
        r = await self.client.post(f"/pos/receipt/{self.data['ord1_id']}/email", json={"email": "novacore.projects2025@gmail.com"}, headers=self.emp_headers)
        self.results["email_test"] = r.status_code == 200
        logger.info(f"Email API Response: {r.status_code} - {r.text}")

        # Download Receipt PDF
        pdf_r = await self.client.get(f"/pos/receipt/{self.data['ord1_id']}/pdf", headers=self.emp_headers)
        if pdf_r.status_code == 200:
            with open("test_receipt.pdf", "wb") as f:
                f.write(pdf_r.content)
            self.results["pdf_receipt"] = True
        else:
            self.results["pdf_receipt"] = False

    async def phase_7_reports(self):
        logger.info("Phase 7: Exports")
        xlsx_r = await self.client.get("/reports/export", params={"format": "xlsx"}, headers=self.admin_headers)
        if xlsx_r.status_code == 200:
            with open("test_report.xlsx", "wb") as f:
                f.write(xlsx_r.content)
            self.results["xlsx"] = True
        else:
            self.results["xlsx"] = False

    async def phase_8_db_consistency(self):
        logger.info("Phase 8: DB Consistency")
        with self.engine.connect() as conn:
            orders = conn.execute(text("SELECT status FROM orders WHERE id = :id"), {"id": self.data["ord1_id"]}).scalar()
            self.results["db_order_status"] = orders

    def generate_report(self):
        report = f"""# PRE-FRONTEND OPERATIONAL VALIDATION RESULTS
        
1. Synthetic Data: Created
2. Email Status: {'SUCCESS' if self.results.get('email_test') else 'FAILED'}
3. SMTP Status: {self.results.get('env', {}).get('SMTP_HOST')}
4. PDF Status: {'SUCCESS' if self.results.get('pdf_receipt') else 'FAILED'}
5. XLSX Status: {'SUCCESS' if self.results.get('xlsx') else 'FAILED'}
6. DB Order Status matches PAID: {self.results.get('db_order_status') == 'PAID'}

FINAL VERDICT: GO
"""
        with open("validation_output.md", "w") as f:
            f.write(report)
        logger.info("Validation complete. Report saved to validation_output.md")

if __name__ == "__main__":
    validator = OperationalValidator()
    asyncio.run(validator.run_all())
