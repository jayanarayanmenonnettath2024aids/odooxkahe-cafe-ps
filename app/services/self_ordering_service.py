"""
Self-ordering service — customer QR-based ordering flow.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.websocket_manager import WSEventType, ws_manager
from app.models.order import KitchenStatus, OrderStatus
from app.models.table import TableStatus
from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderItemRepository, OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.table_repository import TableRepository
from app.schemas.self_ordering import SelfOrderPlaceRequest, SelfOrderStatusResponse
from app.schemas.store_setting import StoreSettingUpdateRequest
from app.services.coupon_service import CouponService
from sqlalchemy import select
from app.models.store_setting import StoreSetting


class SelfOrderingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.table_repo = TableRepository(db)
        self.order_repo = OrderRepository(db)
        self.item_repo = OrderItemRepository(db)
        self.product_repo = ProductRepository(db)
        self.session_repo = SessionRepository(db)
        self.customer_repo = CustomerRepository(db)

    async def get_table_by_token(self, token: str) -> dict:
        """Lookup table by QR token."""
        table = await self.table_repo.get_by_token(token)
        if not table:
            raise NotFoundException("Table", f"token={token}")
        return {
            "table_id": table.id,
            "table_number": table.table_number,
            "floor_name": table.floor.name if table.floor else None,
            "status": table.active_status.value,
        }

    async def get_store_setting(self) -> StoreSetting:
        result = await self.db.execute(select(StoreSetting).order_by(StoreSetting.id))
        setting = result.scalars().first()
        if not setting:
            setting = StoreSetting()
            self.db.add(setting)
            await self.db.commit()
            await self.db.refresh(setting)
        return setting

    async def update_store_setting(self, data: StoreSettingUpdateRequest) -> StoreSetting:
        setting = await self.get_store_setting()
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(setting, key, value)
        await self.db.commit()
        await self.db.refresh(setting)
        return setting

    async def place_order(self, data: SelfOrderPlaceRequest) -> SelfOrderStatusResponse:
        """Customer places order via self-ordering."""
        # Validate table
        table = await self.table_repo.get_by_token(data.table_token)
        if not table:
            raise NotFoundException("Table", f"token={data.table_token}")

        # Get active session
        session = await self.session_repo.get_open_session()
        if not session:
            raise BadRequestException("No active POS session. Please ask staff for help.")

        # Create or find customer
        customer_id = None
        if data.customer_name:
            customer = await self.customer_repo.create({
                "name": data.customer_name,
                "phone": data.customer_phone,
            })
            customer_id = customer.id

        # Create order
        order_number = await self.order_repo.get_next_order_number(session.id)
        order = await self.order_repo.create({
            "order_number": order_number,
            "session_id": session.id,
            "table_id": table.id,
            "customer_id": customer_id,
            "employee_id": session.opened_by,  # Default to session opener
            "status": OrderStatus.DRAFT,
        })

        # Add items
        subtotal = 0.0
        total_tax = 0.0
        for cart_item in data.items:
            product = await self.product_repo.get_by_id(cart_item.product_id)
            if not product or not product.is_active:
                continue

            unit_price = float(product.price)
            tax = round(unit_price * cart_item.quantity * float(product.tax_percentage) / 100, 2)
            line_total = round(unit_price * cart_item.quantity + tax, 2)

            await self.item_repo.create({
                "order_id": order.id,
                "product_id": cart_item.product_id,
                "quantity": cart_item.quantity,
                "unit_price": unit_price,
                "tax_amount": tax,
                "line_total": line_total,
                "kitchen_status": KitchenStatus.TO_COOK,
            })
            subtotal += unit_price * cart_item.quantity
            total_tax += tax

        # Apply coupon if provided
        discount = 0.0
        if data.coupon_code:
            coupon_service = CouponService(self.db)
            from app.schemas.coupon import CouponValidateRequest

            validation = await coupon_service.validate(
                CouponValidateRequest(code=data.coupon_code, order_total=subtotal)
            )
            if validation.valid:
                discount = validation.discount_amount
                order.coupon_id = validation.coupon.id

        # Update order totals
        order.subtotal = subtotal
        order.tax_amount = total_tax
        order.discount_amount = discount
        order.total_amount = subtotal + total_tax - discount
        order.status = OrderStatus.SENT_TO_KITCHEN
        await self.db.flush()

        # Update table status
        await self.table_repo.update_status(table.id, TableStatus.OCCUPIED)

        # Broadcast to KDS
        full_order = await self.order_repo.get_full_order(order.id)
        await ws_manager.broadcast_to_channel("kds", WSEventType.ORDER_SENT_TO_KITCHEN, {
            "order_id": order.id,
            "order_number": order.order_number,
            "table_number": table.table_number,
            "items": [
                {"product": item.product.name, "quantity": item.quantity}
                for item in full_order.items
            ],
            "source": "self_ordering",
        })

        return SelfOrderStatusResponse(
            order_id=order.id,
            order_number=order.order_number,
            status=order.status,
            total_amount=float(order.total_amount),
        )

    async def track_order(self, order_id: int) -> SelfOrderStatusResponse:
        """Track order status for self-ordering customer."""
        order = await self.order_repo.get_full_order(order_id)
        if not order:
            raise NotFoundException("Order", order_id)

        return SelfOrderStatusResponse(
            order_id=order.id,
            order_number=order.order_number,
            status=order.status,
            items=[
                {
                    "product_name": item.product.name if item.product else "",
                    "quantity": item.quantity,
                    "price": float(item.unit_price),
                    "kitchen_status": item.kitchen_status.value,
                }
                for item in order.items
            ],
            total_amount=float(order.total_amount),
        )
