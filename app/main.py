"""
FastAPI application factory — registers all routers, middleware, and startup events.
"""

import logging
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.core.middleware import setup_middleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

settings = get_settings()


def create_app() -> FastAPI:
    application = FastAPI(
        title=f"{settings.APP_NAME} API",
        description="Odoo-style Cafe POS Backend System",
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Middleware
    setup_middleware(application)

    # Register all routers
    from app.api.auth.router import router as auth_router
    from app.api.products.router import router as products_router
    from app.api.categories.router import router as categories_router
    from app.api.floors.router import router as floors_router
    from app.api.tables.router import router as tables_router
    from app.api.employees.router import router as employees_router
    from app.api.customers.router import router as customers_router
    from app.api.orders.router import router as payment_methods_router
    from app.api.coupons.router import router as coupons_router
    from app.api.promotions.router import router as promotions_router
    from app.api.pos.router import router as pos_router
    from app.api.kds.router import router as kds_router
    from app.api.payments.router import router as payments_router
    from app.api.customer_display.router import router as display_router
    from app.api.self_ordering.router import router as self_ordering_router
    from app.api.reports.router import router as reports_router
    from app.api.websocket.router import router as ws_router
    from app.api.bookings.router import router as bookings_router

    application.include_router(auth_router)
    application.include_router(products_router)
    application.include_router(categories_router)
    application.include_router(floors_router)
    application.include_router(tables_router)
    application.include_router(employees_router)
    application.include_router(customers_router)
    application.include_router(payment_methods_router)
    application.include_router(coupons_router)
    application.include_router(promotions_router)
    application.include_router(pos_router)
    application.include_router(kds_router)
    application.include_router(payments_router)
    application.include_router(display_router)
    application.include_router(self_ordering_router)
    application.include_router(reports_router)
    application.include_router(ws_router)
    application.include_router(bookings_router)

    # Static files for QR codes
    qr_dir = os.path.join(os.getcwd(), "generated_qr")
    os.makedirs(qr_dir, exist_ok=True)
    application.mount("/static/qr", StaticFiles(directory=qr_dir), name="qr_codes")

    # Health check
    @application.get("/health", tags=["System"])
    async def health_check():
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

    # Exception Handlers
    @application.exception_handler(IntegrityError)
    async def sqlalchemy_integrity_error_handler(request, exc: IntegrityError):
        # We can analyze the error message to distinguish between UniqueViolation and ForeignKeyViolation
        # For simplicity, returning 400 Bad Request to prevent 500 crashes
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Database integrity error. This may be caused by a duplicate entry or invalid reference.",
                "detail": str(exc.orig) if hasattr(exc, "orig") else str(exc)
            }
        )

    return application


app = create_app()
