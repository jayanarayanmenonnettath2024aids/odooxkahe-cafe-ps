"""
Integration tests for API endpoints.
Tests auth flow, CRUD operations, and order lifecycle.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthAPI:
    """Test authentication endpoints."""

    async def test_signup(self, client: AsyncClient):
        response = await client.post("/auth/signup", json={
            "name": "New User",
            "email": "newuser@test.com",
            "password": "password123",
            "role": "EMPLOYEE",
        })
        print(response.json()); assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "newuser@test.com"

    async def test_signup_duplicate_email(self, client: AsyncClient):
        await client.post("/auth/signup", json={
            "name": "User 1",
            "email": "duplicate@test.com",
            "password": "pass123",
        })
        response = await client.post("/auth/signup", json={
            "name": "User 2",
            "email": "duplicate@test.com",
            "password": "pass456",
        })
        assert response.status_code == 409

    async def test_login(self, client: AsyncClient, admin_token: str):
        # Admin was created by admin_token fixture
        response = await client.post("/auth/login", json={
            "email": "testadmin@test.com",
            "password": "admin123",
        })
        print(response.json()); assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_login_wrong_password(self, client: AsyncClient, admin_token: str):
        response = await client.post("/auth/login", json={
            "email": "testadmin@test.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    async def test_get_me(self, client: AsyncClient, admin_headers: dict):
        print("HEADERS:", admin_headers)
        response = await client.get("/auth/me", headers=admin_headers)
        print(response.json())
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["email"] == "testadmin@test.com"

    async def test_refresh_token(self, client: AsyncClient, admin_token: str):
        # Get refresh token
        login_resp = await client.post("/auth/login", json={
            "email": "testadmin@test.com",
            "password": "admin123",
        })
        refresh_token = login_resp.json()["refresh_token"]

        response = await client.post("/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        print(response.json()); assert response.status_code == 200
        assert "access_token" in response.json()


@pytest.mark.asyncio
class TestCategoryAPI:
    """Test category CRUD."""

    async def test_create_category(self, client: AsyncClient, admin_headers: dict):
        response = await client.post("/categories", json={
            "name": "Hot Drinks",
            "color": "#FF0000",
        }, headers=admin_headers)
        print(response.json()); assert response.status_code == 200
        assert response.json()["data"]["name"] == "Hot Drinks"

    async def test_list_categories(self, client: AsyncClient, admin_headers: dict):
        await client.post("/categories", json={"name": "Cat1"}, headers=admin_headers)
        await client.post("/categories", json={"name": "Cat2"}, headers=admin_headers)

        response = await client.get("/categories")
        print(response.json()); assert response.status_code == 200
        assert len(response.json()["data"]) >= 2


@pytest.mark.asyncio
class TestProductAPI:
    """Test product CRUD."""

    async def test_create_product(self, client: AsyncClient, admin_headers: dict):
        # Create category first
        cat_resp = await client.post("/categories", json={"name": "Beverages"}, headers=admin_headers)
        cat_id = cat_resp.json()["data"]["id"]

        response = await client.post("/products", json={
            "name": "Espresso",
            "price": 120,
            "tax_percentage": 5,
            "category_id": cat_id,
        }, headers=admin_headers)
        print(response.json()); assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "Espresso"
        assert data["price"] == 120

    async def test_search_products(self, client: AsyncClient, admin_headers: dict):
        await client.post("/products", json={
            "name": "Cappuccino",
            "price": 180,
        }, headers=admin_headers)

        response = await client.get("/products?search=cappuccino")
        print(response.json()); assert response.status_code == 200


@pytest.mark.asyncio
class TestFloorAndTableAPI:
    """Test floor and table CRUD."""

    async def test_create_floor_and_tables(self, client: AsyncClient, admin_headers: dict):
        # Create floor
        floor_resp = await client.post("/floors", json={"name": "Ground Floor"}, headers=admin_headers)
        assert floor_resp.status_code == 200
        floor_id = floor_resp.json()["data"]["id"]

        # Create table
        table_resp = await client.post("/tables", json={
            "floor_id": floor_id,
            "table_number": "T01",
            "seat_count": 4,
        }, headers=admin_headers)
        assert table_resp.status_code == 200
        table_data = table_resp.json()["data"]
        assert table_data["table_number"] == "T01"
        assert "unique_token" in table_data

    async def test_get_tables_by_floor(self, client: AsyncClient, admin_headers: dict):
        floor_resp = await client.post("/floors", json={"name": "Floor 1"}, headers=admin_headers)
        floor_id = floor_resp.json()["data"]["id"]

        await client.post("/tables", json={"floor_id": floor_id, "table_number": "T1"}, headers=admin_headers)
        await client.post("/tables", json={"floor_id": floor_id, "table_number": "T2"}, headers=admin_headers)

        response = await client.get(f"/tables/by-floor/{floor_id}")
        print(response.json()); assert response.status_code == 200
        assert len(response.json()["data"]) >= 2


@pytest.mark.asyncio
class TestHealthCheck:
    """Test system health endpoint."""

    async def test_health(self, client: AsyncClient):
        response = await client.get("/health")
        print(response.json()); assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
class TestRBAC:
    """Test role-based access control."""

    async def test_employee_cannot_create_category(self, client: AsyncClient, employee_headers: dict):
        response = await client.post("/categories", json={"name": "Test"}, headers=employee_headers)
        assert response.status_code == 403

    async def test_unauthenticated_cannot_access_protected(self, client: AsyncClient):
        response = await client.get("/auth/me")
        assert response.status_code in (401, 403)
