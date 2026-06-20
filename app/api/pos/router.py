"""
POS Terminal router — maps to POS UI screens.

Floor popup, table selection, products, cart, customer, discount, send to kitchen, order summary, session.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import EmployeeUser
from app.schemas.category import CategoryResponse
from app.schemas.common import SuccessResponse
from app.schemas.order import (
    ApplyCouponRequest,
    ApplyPromotionRequest,
    AssignCustomerRequest,
    CartAddProductRequest,
    CartRemoveProductRequest,
    CartRemoveProductRequest,
    CartUpdateQuantityRequest,
    CloseSessionRequest,
    CreateOrderRequest,
    OpenSessionRequest,
    OrderResponse,
    OrderSummaryResponse,
    SelectTableRequest,
    SendToKitchenRequest,
    SessionResponse,
)
from app.schemas.product import ProductResponse
from app.schemas.table import TableResponse
from app.services.category_service import CategoryService
from app.services.floor_service import FloorService
from app.services.order_service import OrderService
from app.services.product_service import ProductService
from app.services.session_service import SessionService
from app.services.table_service import TableService

router = APIRouter(prefix="/pos", tags=["POS Terminal"])


# ── Session ──────────────────────────────────────────────────────

@router.post("/session/open", response_model=SuccessResponse[SessionResponse])
async def open_session(data: OpenSessionRequest, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = SessionService(db)
    session = await service.open_session(user.id, data)
    return SuccessResponse(data=session, message="Session opened")


@router.post("/session/close", response_model=SuccessResponse[SessionResponse])
async def close_session(data: CloseSessionRequest, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = SessionService(db)
    session = await service.close_session(data)
    return SuccessResponse(data=session, message="Session closed")


@router.get("/session/current", response_model=SuccessResponse[SessionResponse])
async def get_current_session(user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = SessionService(db)
    return SuccessResponse(data=await service.get_current_session())


@router.get("/sessions", response_model=SuccessResponse[list[SessionResponse]])
async def list_sessions(user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = SessionService(db)
    return SuccessResponse(data=await service.get_all_sessions())


# ── Floor Popup ──────────────────────────────────────────────────

@router.get("/floors")
async def get_pos_floors(user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = FloorService(db)
    return SuccessResponse(data=await service.get_all())


@router.get("/floors/{floor_id}/tables", response_model=SuccessResponse[list[TableResponse]])
async def get_floor_tables(floor_id: int, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = TableService(db)
    return SuccessResponse(data=await service.get_by_floor(floor_id))


# ── Table Selection ──────────────────────────────────────────────

@router.post("/select-table")
async def select_table(data: SelectTableRequest, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    result = await service.select_table(data, user.id)
    return SuccessResponse(data=result)


@router.post("/create-order")
async def create_order(data: CreateOrderRequest, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    result = await service.create_order(data, user.id)
    return SuccessResponse(data=result)


# ── Product Section ──────────────────────────────────────────────

@router.get("/products", response_model=SuccessResponse[list[ProductResponse]])
async def get_pos_products(
    category_id: Optional[int] = Query(None),
    user = Depends(EmployeeUser),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    return SuccessResponse(data=await service.get_all(category_id))


@router.get("/categories", response_model=SuccessResponse[list[CategoryResponse]])
async def get_pos_categories(user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = CategoryService(db)
    return SuccessResponse(data=await service.get_all())


@router.get("/products/search", response_model=SuccessResponse[list[ProductResponse]])
async def search_pos_products(
    q: str = Query(...),
    category_id: Optional[int] = Query(None),
    user = Depends(EmployeeUser),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    return SuccessResponse(data=await service.search(q, category_id))


# ── Cart ─────────────────────────────────────────────────────────

@router.post("/cart/add-product", response_model=SuccessResponse[OrderResponse])
async def cart_add_product(data: CartAddProductRequest, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    return SuccessResponse(data=await service.add_product(data))


@router.patch("/cart/update-quantity", response_model=SuccessResponse[OrderResponse])
async def cart_update_quantity(data: CartUpdateQuantityRequest, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    return SuccessResponse(data=await service.update_quantity(data))


@router.delete("/cart/remove-product", response_model=SuccessResponse[OrderResponse])
async def cart_remove_product(data: CartRemoveProductRequest, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    return SuccessResponse(data=await service.remove_product(data.order_item_id))


@router.get("/cart/{order_id}", response_model=SuccessResponse[OrderResponse])
async def get_cart(order_id: int, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    return SuccessResponse(data=await service.get_cart(order_id))


# ── Customer ─────────────────────────────────────────────────────

@router.post("/order/assign-customer", response_model=SuccessResponse[OrderResponse])
async def assign_customer(data: AssignCustomerRequest, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    return SuccessResponse(data=await service.assign_customer(data.order_id, data.customer_id))


# ── Discount ─────────────────────────────────────────────────────

@router.post("/order/apply-coupon", response_model=SuccessResponse[OrderResponse])
async def apply_coupon(data: ApplyCouponRequest, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    return SuccessResponse(data=await service.apply_coupon(data))


@router.post("/order/apply-promotion", response_model=SuccessResponse[OrderResponse])
async def apply_promotion(data: ApplyPromotionRequest, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    return SuccessResponse(data=await service.apply_promotion(data))


# ── Send To Kitchen ──────────────────────────────────────────────

@router.post("/order/send-to-kitchen", response_model=SuccessResponse[OrderResponse])
async def send_to_kitchen(data: SendToKitchenRequest, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    return SuccessResponse(data=await service.send_to_kitchen(data.order_id), message="Order sent to kitchen")


# ── Order Summary ────────────────────────────────────────────────

@router.get("/order-summary/{order_id}", response_model=SuccessResponse[OrderSummaryResponse])
async def get_order_summary(order_id: int, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    return SuccessResponse(data=await service.get_order_summary(order_id))


# ── Receipts ─────────────────────────────────────────────────────

@router.get("/receipt/{order_id}/pdf")
async def download_receipt_pdf(order_id: int, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    from app.utils.receipt import generate_receipt_pdf
    import io

    service = OrderService(db)
    order = await service.get_cart(order_id)  # Using get_cart to fetch full order details

    pdf_bytes = generate_receipt_pdf(order.model_dump())
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=receipt_{order.order_number}.pdf"}
    )


class EmailReceiptRequest(BaseModel):
    email: str

@router.post("/receipt/{order_id}/email", response_model=SuccessResponse)
async def email_receipt(order_id: int, data: EmailReceiptRequest, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    from app.utils.receipt import generate_receipt_pdf
    from app.services.email_service import EmailService

    service = OrderService(db)
    order = await service.get_cart(order_id)
    
    pdf_bytes = generate_receipt_pdf(order.model_dump())
    
    success = await EmailService.send_receipt_email(
        customer_email=data.email,
        order_data=order.model_dump(),
        pdf_bytes=pdf_bytes
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email")
        
    return SuccessResponse(message=f"Receipt sent to {data.email}")
