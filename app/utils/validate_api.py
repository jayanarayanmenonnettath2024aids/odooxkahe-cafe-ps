import asyncio
import httpx
from pprint import pprint
from app.main import app

BASE_URL = "http://testserver"

async def validate_api():
    print("Starting Database vs API Validation...")
    
    # We must explicitly construct the transport with the async ASGI app.
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=BASE_URL) as client:
        # 1. Login
        print("\n--- 1. Testing Auth & Login ---")
        login_data = {
            "email": "admin@cafepos.com",
            "password": "admin123"
        }
        res = await client.post("/auth/login", json=login_data)
        if res.status_code != 200:
            print(f"Login failed! Status: {res.status_code}")
            print(res.text)
            return
            
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful. Token received.")

        # 2. Fetch Products
        print("\n--- 2. Fetching Products ---")
        res = await client.get("/products", headers=headers)
        if res.status_code == 200:
            data = res.json()
            print(f"Products fetched successfully: {len(data.get('data', []))} products found.")
        else:
            print(f"Failed to fetch products: {res.status_code} - {res.text}")

        # 3. Fetch POS Sessions
        print("\n--- 3. Fetching POS Sessions ---")
        res = await client.get("/pos/sessions", headers=headers)
        if res.status_code == 200:
            data = res.json()
            print(f"POS Sessions fetched successfully: {len(data.get('data', []))} sessions found.")
        else:
            print(f"Failed to fetch POS sessions: {res.status_code} - {res.text}")

        # 4. Fetch Active Orders
        print("\n--- 4. Fetching Active Orders ---")
        res = await client.get("/kds/orders", headers=headers)  # Checking KDS active orders
        if res.status_code == 200:
            data = res.json()
            print(f"Active Orders fetched successfully: {len(data.get('data', []))} active orders found.")
        else:
            print(f"Failed to fetch orders: {res.status_code} - {res.text}")

        # 5. Fetch Reservations
        print("\n--- 5. Fetching Reservations ---")
        res = await client.get("/reservations/", headers=headers)
        if res.status_code == 200:
            data = res.json()
            print(f"Reservations fetched successfully: {len(data.get('data', []))} reservations found.")
        else:
            print(f"Failed to fetch reservations: {res.status_code} - {res.text}")

    print("\nDatabase vs API Validation completed.")

if __name__ == "__main__":
    asyncio.run(validate_api())
