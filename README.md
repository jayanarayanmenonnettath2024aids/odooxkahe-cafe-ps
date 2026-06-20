# ☕ CafePOS — Odoo-Style Cafe POS Backend

Production-quality backend for a Cafe Point-of-Sale system built with **FastAPI**, **PostgreSQL**, **SQLAlchemy 2.0**, **Alembic**, **Pydantic v2**, **JWT Authentication**, and **WebSockets**.

## 🚀 Quick Start

### With Docker (Recommended)

```bash
# Clone and start
docker-compose up -d

# Run migrations
docker-compose exec app alembic upgrade head

# Seed initial data
docker-compose exec app python -m app.utils.seed

# API is live at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### Without Docker

```bash
# Install dependencies
pip install -e ".[dev]"

# Set up PostgreSQL and update .env
cp .env.example .env

# Run migrations
alembic upgrade head

# Seed data
python -m app.utils.seed

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 API Documentation

Interactive docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Architecture

```
Clean Architecture with Repository + Service Layer Pattern

┌─────────────┐   ┌─────────────┐   ┌──────────────┐   ┌──────────────┐
│  API Router  │──▶│   Service   │──▶│  Repository  │──▶│   Database   │
│  (FastAPI)   │   │  (Business) │   │  (Data)      │   │  (PostgreSQL)│
└─────────────┘   └─────────────┘   └──────────────┘   └──────────────┘
       │
       ▼
┌─────────────┐
│  WebSocket  │
│  Manager    │
└─────────────┘
```

## 🔐 Default Credentials

| Role     | Email              | Password     |
|----------|--------------------|--------------|
| Admin    | admin@cafepos.com  | admin123     |
| Employee | john@cafepos.com   | employee123  |

## 🧪 Testing

```bash
pytest app/tests/ -v
```

## 📡 WebSocket Events

Connect to `ws://localhost:8000/ws?channels=kds,pos,tables`

Events: `ORDER_CREATED`, `ORDER_SENT_TO_KITCHEN`, `ORDER_PREPARING`, `ORDER_COMPLETED`, `PAYMENT_SUCCESS`, `KDS_UPDATE`, `TABLE_STATUS_UPDATE`, `SESSION_OPENED`, `SESSION_CLOSED`

## 🎫 Sample Coupons

| Code       | Type       | Value |
|------------|------------|-------|
| WELCOME10  | 10% off    | 10%   |
| FLAT50     | ₹50 off    | ₹50   |
| COFFEE20   | 20% off    | 20%   |
