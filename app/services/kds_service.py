"""
KDS (Kitchen Display System) service — order stage management.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.websocket_manager import WSEventType, ws_manager
from app.models.order import KitchenStatus, OrderStatus
from app.repositories.order_repository import OrderItemRepository, OrderRepository
from app.schemas.kds import KDSOrderItemResponse, KDSOrderResponse


class KDSService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.item_repo = OrderItemRepository(db)

    async def get_kitchen_orders(self) -> list[KDSOrderResponse]:
        """Get all orders visible on KDS."""
        orders = await self.order_repo.get_kitchen_orders_simple()
        return [self._to_kds_response(o) for o in orders]

    async def search_orders(self, query: str) -> list[KDSOrderResponse]:
        orders = await self.order_repo.search_orders(query)
        return [
            self._to_kds_response(o)
            for o in orders
            if o.status in (OrderStatus.SENT_TO_KITCHEN, OrderStatus.PREPARING, OrderStatus.READY)
        ]

    async def advance_order_stage(self, order_id: int) -> KDSOrderResponse:
        """Move an order to the next kitchen stage."""
        order = await self.order_repo.get_full_order(order_id)
        if not order:
            raise NotFoundException("Order", order_id)

        stage_map = {
            OrderStatus.SENT_TO_KITCHEN: OrderStatus.PREPARING,
            OrderStatus.PREPARING: OrderStatus.READY,
        }

        next_status = stage_map.get(order.status)
        if not next_status:
            raise BadRequestException(
                f"Cannot advance order from status '{order.status.value}'"
            )

        order.status = next_status

        # Update all item statuses
        item_status_map = {
            OrderStatus.PREPARING: KitchenStatus.PREPARING,
            OrderStatus.READY: KitchenStatus.COMPLETED,
        }
        if next_status in item_status_map:
            for item in order.items:
                item.kitchen_status = item_status_map[next_status]

        await self.db.flush()

        # Broadcast KDS update
        event = {
            OrderStatus.PREPARING: WSEventType.ORDER_PREPARING,
            OrderStatus.READY: WSEventType.ORDER_COMPLETED,
        }.get(next_status, WSEventType.KDS_UPDATE)

        await ws_manager.broadcast_to_channel("kds", event, {
            "order_id": order.id,
            "order_number": order.order_number,
            "status": next_status.value,
        })

        # Broadcast customer display
        await ws_manager.broadcast_to_channel(
            f"customer:{order.id}", WSEventType.CUSTOMER_DISPLAY_UPDATE,
            {"order_id": order.id, "status": next_status.value},
        )

        full_order = await self.order_repo.get_full_order(order_id)
        return self._to_kds_response(full_order)

    async def complete_item(self, item_id: int) -> KDSOrderItemResponse:
        """Mark a single order item as completed."""
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            raise NotFoundException("OrderItem", item_id)

        item = await self.item_repo.update_kitchen_status(item_id, KitchenStatus.COMPLETED)

        # Check if all items completed — auto-advance order
        order = await self.order_repo.get_full_order(item.order_id)
        if not order:
            raise NotFoundException("Order", item.order_id)
        all_complete = all(i.kitchen_status == KitchenStatus.COMPLETED for i in order.items)
        if all_complete and order.status == OrderStatus.PREPARING:
            order.status = OrderStatus.READY
            await self.db.flush()
            await ws_manager.broadcast_to_channel("kds", WSEventType.ORDER_COMPLETED, {
                "order_id": order.id,
                "order_number": order.order_number,
                "status": "READY",
            })

        await ws_manager.broadcast_to_channel("kds", WSEventType.KDS_UPDATE, {
            "item_id": item_id,
            "kitchen_status": "COMPLETED",
        })

        return KDSOrderItemResponse(
            id=item.id,
            product_name=item.product.name if item.product else "",
            quantity=item.quantity,
            kitchen_status=item.kitchen_status,
        )

    def _to_kds_response(self, order) -> KDSOrderResponse:
        return KDSOrderResponse(
            id=order.id,
            order_number=order.order_number,
            order_type=order.order_type.value if order.order_type else None,
            table_id=order.table_id,
            table_number=order.table.table_number if order.table else None,
            floor_name=order.table.floor.name if order.table and hasattr(order.table, 'floor') and order.table.floor else None,
            status=order.status,
            items=[
                KDSOrderItemResponse(
                    id=item.id,
                    product_name=item.product.name if item.product else "",
                    quantity=item.quantity,
                    kitchen_status=item.kitchen_status,
                )
                for item in order.items
            ],
            created_at=order.created_at,
        )
