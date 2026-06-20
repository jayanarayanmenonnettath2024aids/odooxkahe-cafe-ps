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

@router.get("/orders", response_model=SuccessResponse[list[OrderResponse]])
async def list_pos_orders(limit: int = 100, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    return SuccessResponse(data=await service.get_all_orders(limit))


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

# ── Frontend-Compatible Alias Endpoints ─────────────────────────
# These bridge the gap between what the React frontend calls and the actual backend routes.

class OrderItemInput(BaseModel):
    product_id: int
    quantity: int = 1
    notes: Optional[str] = None

class CreateOrderWithItemsRequest(BaseModel):
    session_id: int
    order_type: str = "TAKEAWAY"
    table_id: Optional[int] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    items: list[OrderItemInput] = []
    discount_amount: float = 0.0
    coupon_id: Optional[int] = None
    promotion_id: Optional[int] = None


@router.post("/orders", response_model=SuccessResponse[OrderResponse])
async def create_order_with_items(
    data: CreateOrderWithItemsRequest,
    user = Depends(EmployeeUser),
    db: AsyncSession = Depends(get_db),
):
    """
    Frontend-compatible endpoint: creates an order and adds all cart items atomically.
    Maps the React frontend's POST /pos/orders call to the backend's create_order + add_product flow.
    """
    from app.schemas.order import CreateOrderRequest, CartAddProductRequest
    from app.models.order import OrderType as OT

    # Normalize order_type string → enum
    type_map = {
        "dine_in": OT.DINE_IN, "DINE_IN": OT.DINE_IN,
        "takeaway": OT.TAKEAWAY, "TAKEAWAY": OT.TAKEAWAY,
        "parcel": OT.PARCEL, "PARCEL": OT.PARCEL,
    }
    order_type = type_map.get(data.order_type, OT.TAKEAWAY)

    service = OrderService(db)

    # Create the base order
    create_req = CreateOrderRequest(
        session_id=data.session_id,
        order_type=order_type,
        table_id=data.table_id,
        customer_name=data.customer_name,
    )
    result = await service.create_order(create_req, user.id)
    order_data = result.get("current_order", {})
    order_id = order_data.get("id")

    if not order_id:
        raise HTTPException(status_code=500, detail="Failed to create order")

    # Assign customer if provided
    if data.customer_id:
        await service.assign_customer(order_id, data.customer_id)

    # Add all cart items
    for item in data.items:
        add_req = CartAddProductRequest(
            order_id=order_id,
            product_id=item.product_id,
            quantity=item.quantity,
        )
        await service.add_product(add_req)

    # Fetch the final order state
    full_order = await service.get_cart(order_id)

    if data.discount_amount > 0 or data.coupon_id or data.promotion_id:
        db_order = await service.order_repo.get_by_id(order_id)
        if db_order:
            db_order.discount_amount = data.discount_amount
            db_order.coupon_id = data.coupon_id
            db_order.promotion_id = data.promotion_id
            db_order.total_amount = max(0.0, float(db_order.subtotal) + float(db_order.tax_amount) - float(data.discount_amount))
            await db.flush()
            full_order = await service.get_cart(order_id)

    return SuccessResponse(data=full_order, message="Order created")


@router.get("/orders/{order_id}", response_model=SuccessResponse[OrderResponse])
async def get_single_order(order_id: int, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    """Get a single order by ID."""
    service = OrderService(db)
    return SuccessResponse(data=await service.get_cart(order_id))


@router.post("/cart/{order_id}/send-to-kitchen", response_model=SuccessResponse[OrderResponse])
async def send_to_kitchen_by_id(order_id: int, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    """Frontend-compatible alias: POST /pos/cart/{order_id}/send-to-kitchen."""
    service = OrderService(db)
    return SuccessResponse(data=await service.send_to_kitchen(order_id), message="Order sent to kitchen")


class UniversalPayRequest(BaseModel):
    payment_method_id: Optional[int] = None
    payment_method_type: Optional[str] = None   # 'cash', 'card', 'upi'
    amount: float
    transaction_reference: Optional[str] = None

@router.post("/receipt/{order_id}/pay", response_model=SuccessResponse)
async def pay_order(
    order_id: int,
    data: UniversalPayRequest,
    user = Depends(EmployeeUser),
    db: AsyncSession = Depends(get_db),
):
    """
    Frontend-compatible universal payment endpoint.
    Automatically sends the order to kitchen if still in DRAFT, then processes payment.
    """
    from app.models.order import OrderStatus
    from app.repositories.order_repository import OrderRepository
    from app.repositories.payment_method_repository import PaymentMethodRepository
    from app.models.payment import PaymentStatus
    from app.repositories.payment_repository import PaymentRepository
    from datetime import datetime, timezone
    from app.models.table import TableStatus
    from app.repositories.table_repository import TableRepository

    order_repo = OrderRepository(db)
    pm_repo = PaymentMethodRepository(db)
    payment_repo = PaymentRepository(db)
    table_repo = TableRepository(db)
    order_service = OrderService(db)

    order = await order_repo.get_full_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status == OrderStatus.PAID:
        raise HTTPException(status_code=400, detail="Order already paid")

    # If order is still DRAFT, auto-advance to SENT_TO_KITCHEN
    if order.status == OrderStatus.DRAFT:
        if not order.items:
            raise HTTPException(status_code=400, detail="Cannot pay an empty order")
        order.status = OrderStatus.SENT_TO_KITCHEN
        await db.flush()

    # Determine payment method type
    pm_type = "cash"
    if data.payment_method_id:
        pm = await pm_repo.get_by_id(data.payment_method_id)
        if pm:
            pm_type = pm.name.lower()  # 'cash', 'card', 'upi'
    elif data.payment_method_type:
        pm_type = data.payment_method_type.lower()

    # Find the payment method record by type
    pm_name_map = {"cash": "CASH", "card": "CARD", "upi": "UPI"}
    pm = await pm_repo.get_by_name(pm_name_map.get(pm_type, "CASH"))
    if not pm:
        # Fallback: try get by id
        if data.payment_method_id:
            pm = await pm_repo.get_by_id(data.payment_method_id)
    if not pm:
        raise HTTPException(status_code=400, detail=f"Payment method '{pm_type}' not configured")

    total = float(order.total_amount or 0)

    # Create payment record
    await payment_repo.create({
        "order_id": order_id,
        "payment_method_id": pm.id,
        "amount": data.amount,
        "transaction_reference": data.transaction_reference or f"TXN-{order_id}-{int(datetime.now(timezone.utc).timestamp())}",
        "status": PaymentStatus.SUCCESS,
        "paid_at": datetime.now(timezone.utc),
    })

    # Mark order as PAID
    order.status = OrderStatus.PAID
    await db.flush()
    await db.commit()

    # Free table if assigned
    if order.table_id:
        await table_repo.update_status(order.table_id, TableStatus.AVAILABLE)

    return SuccessResponse(message=f"Payment of ₹{total:.2f} processed successfully via {pm.name}")

# ── Razorpay Endpoints ───────────────────────────────────────────

class RazorpayCreateOrderRequest(BaseModel):
    amount: float

@router.post("/razorpay/create-order", response_model=SuccessResponse)
async def create_razorpay_order(data: RazorpayCreateOrderRequest, user = Depends(EmployeeUser)):
    """Create a Razorpay order session."""
    import razorpay
    from app.core.config import get_settings
    
    settings = get_settings()
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise HTTPException(status_code=500, detail="Razorpay is not configured")
        
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    try:
        # Amount in paise
        order_data = {
            "amount": int(data.amount * 100),
            "currency": "INR",
            "payment_capture": 1
        }
        rzp_order = client.order.create(data=order_data)
        return SuccessResponse(data={"razorpay_order_id": rzp_order["id"], "amount": rzp_order["amount"], "key": settings.RAZORPAY_KEY_ID})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RazorpayVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

@router.post("/razorpay/verify", response_model=SuccessResponse)
async def verify_razorpay_payment(data: RazorpayVerifyRequest, user = Depends(EmployeeUser)):
    """Verify a successful Razorpay payment signature."""
    import razorpay
    from app.core.config import get_settings
    
    settings = get_settings()
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': data.razorpay_order_id,
            'razorpay_payment_id': data.razorpay_payment_id,
            'razorpay_signature': data.razorpay_signature
        })
        return SuccessResponse(message="Payment verified successfully")
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid payment signature")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
