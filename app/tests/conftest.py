"""
Test fixtures — shared test database and client setup.
"""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.user import User, UserRole

# Use SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient, db_session: AsyncSession) -> str:
    """Create admin user and return access token."""
    admin = User(
        name="Test Admin",
        email="testadmin@test.com",
        password_hash=hash_password("admin123"),
        role=UserRole.ADMIN,
    )
    db_session.add(admin)
    await db_session.commit()

    response = await client.post("/auth/login", json={
        "email": "testadmin@test.com",
        "password": "admin123",
    })
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def employee_token(client: AsyncClient, db_session: AsyncSession) -> str:
    """Create employee user and return access token."""
    emp = User(
        name="Test Employee",
        email="testemp@test.com",
        password_hash=hash_password("emp123"),
        role=UserRole.EMPLOYEE,
    )
    db_session.add(emp)
    await db_session.commit()

    response = await client.post("/auth/login", json={
        "email": "testemp@test.com",
        "password": "emp123",
    })
    return response.json()["access_token"]


@pytest_asyncio.fixture
def admin_headers(admin_token: str) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest_asyncio.fixture
def employee_headers(employee_token: str) -> dict:
    return {"Authorization": f"Bearer {employee_token}"}
