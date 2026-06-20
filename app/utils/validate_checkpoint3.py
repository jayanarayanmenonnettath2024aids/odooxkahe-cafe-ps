import asyncio
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_settings

settings = get_settings()
BASE_URL = "http://testserver"

async def test_checkpoint_3():
    print("Starting Checkpoint 3 Validation: Feature Verification")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=BASE_URL) as client:
        # 1. Login to get token
        print("\n--- Auth ---")
        login_data = {
            "email": "admin@cafepos.com",
            "password": "admin123"
        }
        res = await client.post("/auth/login", json=login_data)
        if res.status_code != 200:
            print(f"Login failed: {res.text}")
            return
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful")

        # Get a valid order ID for tests
        res = await client.get("/kds/orders", headers=headers)
        orders = res.json().get("data", [])
        if not orders:
            print("No active orders found for testing!")
            return
        order_id = orders[0]["id"]
        order_num = orders[0]["order_number"]
        print(f"Picked Order {order_id} ({order_num}) for tests")

        # ---------------------------------------------------------
        # Phase 8: PDF Validation
        # ---------------------------------------------------------
        print("\n--- Phase 8: PDF Validation ---")
        res = await client.get(f"/pos/receipt/{order_id}/pdf", headers=headers)
        if res.status_code == 200 and res.headers["content-type"] == "application/pdf":
            print(f"PDF generated successfully. Size: {len(res.content)} bytes")
        else:
            print(f"PDF generation failed: {res.status_code}")

        # ---------------------------------------------------------
        # Phase 9: Email Validation
        # ---------------------------------------------------------
        print("\n--- Phase 9: Email Validation ---")
        # Send email to the configured SMTP account itself to avoid spamming
        email_data = {"email": settings.SMTP_USERNAME}
        print(f"Sending receipt to {email_data['email']}...")
        res = await client.post(f"/pos/receipt/{order_id}/email", json=email_data, headers=headers)
        if res.status_code == 200:
            print("Email sent successfully (check SMTP credentials account inbox)")
        else:
            print(f"Email sending failed: {res.status_code} - {res.text}")

        # ---------------------------------------------------------
        # Phase 10: Twilio Validation
        # ---------------------------------------------------------
        print("\n--- Phase 10: Twilio Webhook Validation ---")
        # We simulate a Twilio Voice webhook payload
        twilio_payload = {
            "CallSid": "CA1234567890abcdef1234567890abcdef",
            "From": "+1234567890",
            "To": settings.TWILIO_PHONE_NUMBER
        }
        # Twilio sends POST data as application/x-www-form-urlencoded
        res = await client.post("/twilio/incoming", data=twilio_payload)
        if res.status_code == 200 and "<?xml" in res.text:
            print("Twilio Webhook executed successfully. TwiML response generated.")
        else:
            print(f"Twilio Webhook failed: {res.status_code} - {res.text}")

        # ---------------------------------------------------------
        # Phase 12: Reporting Validation
        # ---------------------------------------------------------
        print("\n--- Phase 12: Reporting Validation ---")
        res = await client.get("/reports/dashboard?period=today", headers=headers)
        if res.status_code == 200:
            data = res.json()
            print("Sales Dashboard generated successfully.")
            print(f"   Total Sales: {data['data'].get('total_revenue', 0)}")
        else:
            print(f"Sales Dashboard failed: {res.status_code} - {res.text}")

    # ---------------------------------------------------------
    # Phase 11: WebSocket Validation
    # ---------------------------------------------------------
    print("\n--- Phase 11: WebSocket Validation ---")
    try:
        # We use sync TestClient purely for websocket
        with TestClient(app).websocket_connect("/ws?channels=kds") as websocket:
            print("WebSocket connection established successfully to /ws?channels=kds")
    except Exception as e:
        print(f"WebSocket connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_checkpoint_3())
