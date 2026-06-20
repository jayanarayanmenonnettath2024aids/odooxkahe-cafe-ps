"""
Order service — full order lifecycle management.

Handles: create order, add/update/remove items, apply discounts,
         send to kitchen, state transitions, order summary.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestException,
    InvalidStateTransitionException,
    NotFoundException,
    SessionNotOpenException,
)
from app.core.websocket_manager import WSEventType, ws_manager
from app.models.order import ORDER_TRANSITIONS, KitchenStatus, Order, OrderItem, OrderStatus
from app.models.table import TableStatus
from app.repositories.coupon_repository import CouponRepository
from app.repositories.order_repository import OrderItemRepository, OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.promotion_repository import PromotionRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.table_repository import TableRepository
from app.schemas.order import (
    ApplyCouponRequest,
    ApplyPromotionRequest,
    CartAddProductRequest,
    CartUpdateQuantityRequest,
    OrderItemResponse,
    OrderResponse,
    OrderSummaryResponse,
    SelectTableRequest,
)
from app.services.coupon_service import CouponService
from app.services.promotion_service import PromotionService

logger = logging.getLogger("cafepos.order")


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.item_repo = OrderItemRepository(db)
        self.product_repo = ProductRepository(db)
        self.table_repo = TableRepository(db)
        self.session_repo = SessionRepository(db)
        self.coupon_repo = CouponRepository(db)
        self.promo_repo = PromotionRepository(db)

    # ── Table Selection ─────────────────────────────────────────────

    async def select_table(self, data: SelectTableRequest, employee_id: int) -> dict:
        """Select a table and create/return order for it."""
        # Validate session
        session = await self.session_repo.get_by_id(data.session_id)
        if not session or session.status.value != "OPEN":
            raise SessionNotOpenException()

        # Validate table
        table = await self.table_repo.get_by_id(data.table_id)
        if not table:
            raise NotFoundException("Table", data.table_id)

        # Check for existing active order on table
        existing_order = await self.order_repo.get_by_table_active(data.table_id)

        if existing_order:
            return {
                "table": self._table_dict(table),
                "current_order": self._to_response(existing_order).model_dump(),
                "table_status": table.active_status.value,
            }

        # Create new DRAFT order
        order_number = await self.order_repo.get_next_order_number(data.session_id)
        order = await self.order_repo.create({
            "order_number": order_number,
            "session_id": data.session_id,
            "table_id": data.table_id,
            "employee_id": employee_id,
            "status": OrderStatus.DRAFT,
        })

        # Mark table as occupied
        await self.table_repo.update_status(data.table_id, TableStatus.OCCUPIED)

        # Broadcast table status
        await ws_manager.broadcast_to_channel("tables", WSEventType.TABLE_STATUS_UPDATE, {
            "table_id": data.table_id,
            "status": "OCCUPIED",
        })

        order = await self.order_repo.get_full_order(order.id)
        return {
            "table": self._table_dict(table),
            "current_order": self._to_response(order).model_dump(),
            "table_status": "OCCUPIED",
        }

    # ── Cart Operations ─────────────────────────────────────────────

    async def add_product(self, data: CartAddProductRequest) -> OrderResponse:
        """Add a product to the order cart."""
        order = await self.order_repo.get_by_id(data.order_id)
        if not order:
            raise NotFoundException("Order", data.order_id)
        if order.status != OrderStatus.DRAFT:
            raise BadRequestException("Can only add products to DRAFT orders")

        product = await self.product_repo.get_by_id(data.product_id)
        if not product:
            raise NotFoundException("Product", data.product_id)

        # Check if product already in order — update quantity
        existing_item = None
        items = await self.item_repo.get_items_by_order(data.order_id)
        for item in items:
            if item.product_id == data.product_id:
                existing_item = item
                break

        if existing_item:
            existing_item.quantity += data.quantity
            existing_item.line_total = self._calc_line_total(
                float(existing_item.unit_price),
                existing_item.quantity,
                float(product.tax_percentage),
            )
            existing_item.tax_amount = self._calc_item_tax(
                float(existing_item.unit_price),
                existing_item.quantity,
                float(product.tax_percentage),
            )
            await self.db.flush()
        else:
            unit_price = float(product.price)
            tax_amount = self._calc_item_tax(unit_price, data.quantity, float(product.tax_percentage))
            line_total = self._calc_line_total(unit_price, data.quantity, float(product.tax_percentage))

            await self.item_repo.create({
                "order_id": data.order_id,
                "product_id": data.product_id,
                "quantity": data.quantity,
                "unit_price": unit_price,
                "tax_amount": tax_amount,
                "line_total": line_total,
                "kitchen_status": KitchenStatus.TO_COOK,
            })

        # Recalculate totals
        await self._recalculate_order(data.order_id)

        full_order = await self.order_repo.get_full_order(data.order_id)
        return self._to_response(full_order)

    async def update_quantity(self, data: CartUpdateQuantityRequest) -> OrderResponse:
        """Update item quantity. Set to 0 to remove."""
        item = await self.item_repo.get_by_id(data.order_item_id)
        if not item:
            raise NotFoundException("OrderItem", data.order_item_id)

        order = await self.order_repo.get_by_id(item.order_id)
        if order.status != OrderStatus.DRAFT:
            raise BadRequestException("Can only modify DRAFT orders")

        if data.quantity == 0:
            await self.item_repo.delete(data.order_item_id)
        else:
            product = await self.product_repo.get_by_id(item.product_id)
            item.quantity = data.quantity
            item.tax_amount = self._calc_item_tax(
                float(item.unit_price), data.quantity, float(product.tax_percentage)
            )
            item.line_total = self._calc_line_total(
                float(item.unit_price), data.quantity, float(product.tax_percentage)
            )
            await self.db.flush()

        await self._recalculate_order(item.order_id)
        full_order = await self.order_repo.get_full_order(item.order_id)
        return self._to_response(full_order)

    async def remove_product(self, order_item_id: int) -> OrderResponse:
        """Remove an item from the order."""
        item = await self.item_repo.get_by_id(order_item_id)
        if not item:
            raise NotFoundException("OrderItem", order_item_id)

        order = await self.order_repo.get_by_id(item.order_id)
        if order.status != OrderStatus.DRAFT:
            raise BadRequestException("Can only modify DRAFT orders")

        order_id = item.order_id
        await self.item_repo.delete(order_item_id)
        await self._recalculate_order(order_id)

        full_order = await self.order_repo.get_full_order(order_id)
        return self._to_response(full_order)

    async def get_cart(self, order_id: int) -> OrderResponse:
        """Get current cart/order details."""
        order = await self.order_repo.get_full_order(order_id)
        if not order:
            raise NotFoundException("Order", order_id)
        return self._to_response(order)

    # ── Customer & Discounts ────────────────────────────────────────

    async def assign_customer(self, order_id: int, customer_id: int) -> OrderResponse:
        """Assign a customer to an order."""
        order = await self.order_repo.update(order_id, {"customer_id": customer_id})
        if not order:
            raise NotFoundException("Order", order_id)
        full_order = await self.order_repo.get_full_order(order_id)
        return self._to_response(full_order)

    async def apply_coupon(self, data: ApplyCouponRequest) -> OrderResponse:
        """Apply a coupon to an order."""
        order = await self.order_repo.get_full_order(data.order_id)
        if not order:
            raise NotFoundException("Order", data.order_id)

        coupon_service = CouponService(self.db)
        from app.schemas.coupon import CouponValidateRequest

        validation = await coupon_service.validate(
            CouponValidateRequest(code=data.coupon_code, order_total=float(order.subtotal))
        )
        if not validation.valid:
            raise BadRequestException(validation.message)

        order.coupon_id = validation.coupon.id
        order.discount_amount = validation.discount_amount
        order.total_amount = float(order.subtotal) + float(order.tax_amount) - validation.discount_amount
        await self.db.flush()

        full_order = await self.order_repo.get_full_order(data.order_id)
        return self._to_response(full_order)

    async def apply_promotion(self, data: ApplyPromotionRequest) -> OrderResponse:
        """Apply a promotion to an order."""
        order = await self.order_repo.get_full_order(data.order_id)
        if not order:
            raise NotFoundException("Order", data.order_id)

        promotion = await self.promo_repo.get_by_id(data.promotion_id)
        if not promotion or not promotion.is_active:
            raise BadRequestException("Promotion not found or inactive")

        total_qty = sum(item.quantity for item in order.items)
        discount = PromotionService.calculate_promotion_discount(
            promotion, float(order.subtotal), total_qty
        )

        if discount <= 0:
            raise BadRequestException("Order does not meet promotion requirements")

        order.promotion_id = data.promotion_id
        order.discount_amount = discount
        order.total_amount = float(order.subtotal) + float(order.tax_amount) - discount
        await self.db.flush()

        full_order = await self.order_repo.get_full_order(data.order_id)
        return self._to_response(full_order)

    # ── Kitchen Operations ──────────────────────────────────────────

    async def send_to_kitchen(self, order_id: int) -> OrderResponse:
        """Send order to kitchen — changes status and broadcasts WS event."""
        order = await self.order_repo.get_full_order(order_id)
        if not order:
            raise NotFoundException("Order", order_id)

        self._validate_transition(order.status, OrderStatus.SENT_TO_KITCHEN)

        if not order.items:
            raise BadRequestException("Cannot send empty order to kitchen")

        order.status = OrderStatus.SENT_TO_KITCHEN
        await self.db.flush()

        # Broadcast
        await ws_manager.broadcast_to_channel("kds", WSEventType.ORDER_SENT_TO_KITCHEN, {
            "order_id": order.id,
            "order_number": order.order_number,
            "table_number": order.table.table_number if order.table else None,
            "items": [
                {"product": item.product.name, "quantity": item.quantity}
                for item in order.items
            ],
        })

        await ws_manager.broadcast_to_channel(
            f"customer:{order.id}", WSEventType.CUSTOMER_DISPLAY_UPDATE,
            {"order_id": order.id, "status": "SENT_TO_KITCHEN"},
        )

        full_order = await self.order_repo.get_full_order(order_id)
        return self._to_response(full_order)

    # ── Order Summary ───────────────────────────────────────────────

    async def get_order_summary(self, order_id: int) -> OrderSummaryResponse:
        order = await self.order_repo.get_full_order(order_id)
        if not order:
            raise NotFoundException("Order", order_id)
        return OrderSummaryResponse(
            order_id=order.id,
            order_number=order.order_number,
            subtotal=float(order.subtotal),
            tax_amount=float(order.tax_amount),
            discount_amount=float(order.discount_amount),
            total_amount=float(order.total_amount),
            item_count=sum(item.quantity for item in order.items),
            status=order.status,
        )

    # ── Internal Helpers ────────────────────────────────────────────

    async def _recalculate_order(self, order_id: int):
        """Recalculate subtotal, tax, and total for an order."""
        items = await self.item_repo.get_items_by_order(order_id)
        subtotal = sum(float(item.unit_price) * item.quantity for item in items)
        tax = sum(float(item.tax_amount) for item in items)

        order = await self.order_repo.get_by_id(order_id)
        order.subtotal = subtotal
        order.tax_amount = tax
        order.total_amount = subtotal + tax - float(order.discount_amount)
        await self.db.flush()

    def _validate_transition(self, current: OrderStatus, target: OrderStatus):
        allowed = ORDER_TRANSITIONS.get(current, [])
        if target not in allowed:
            raise InvalidStateTransitionException(current.value, target.value)

    def _calc_item_tax(self, unit_price: float, quantity: int, tax_pct: float) -> float:
        return round(unit_price * quantity * tax_pct / 100, 2)

    def _calc_line_total(self, unit_price: float, quantity: int, tax_pct: float) -> float:
        base = unit_price * quantity
        tax = self._calc_item_tax(unit_price, quantity, tax_pct)
        return round(base + tax, 2)

    def _to_response(self, order: Order) -> OrderResponse:
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            session_id=order.session_id,
            table_id=order.table_id,
            table_number=order.table.table_number if order.table else None,
            customer_id=order.customer_id,
            customer_name=order.customer.name if order.customer else None,
            employee_id=order.employee_id,
            employee_name=order.employee.name if order.employee else None,
            status=order.status,
            subtotal=float(order.subtotal),
            tax_amount=float(order.tax_amount),
            discount_amount=float(order.discount_amount),
            total_amount=float(order.total_amount),
            items=[self._item_response(i) for i in order.items],
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

    def _item_response(self, item: OrderItem) -> OrderItemResponse:
        return OrderItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product.name if item.product else None,
            quantity=item.quantity,
            unit_price=float(item.unit_price),
            tax_amount=float(item.tax_amount),
            discount_amount=float(item.discount_amount),
            line_total=float(item.line_total),
            kitchen_status=item.kitchen_status,
        )

    def _table_dict(self, table) -> dict:
        return {
            "id": table.id,
            "floor_id": table.floor_id,
            "table_number": table.table_number,
            "seat_count": table.seat_count,
            "active_status": table.active_status.value,
            "unique_token": table.unique_token,
        }
