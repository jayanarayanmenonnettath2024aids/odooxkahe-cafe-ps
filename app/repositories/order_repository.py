"""
Order and OrderItem repositories.
"""

from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import KitchenStatus, Order, OrderItem, OrderStatus
from app.models.table import Table
from app.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: AsyncSession):
        super().__init__(Order, db)

    async def get_full_order(self, order_id: int) -> Optional[Order]:
        """Get order with all relationships loaded."""
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product),
                selectinload(Order.table),
                selectinload(Order.customer),
                selectinload(Order.employee),
                selectinload(Order.payments),
            )
            .where(Order.id == order_id)
        )
        return result.scalars().first()

    async def get_by_table_active(self, table_id: int) -> Optional[Order]:
        """Get the current active (non-paid, non-cancelled) order for a table."""
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product),
                selectinload(Order.table),
                selectinload(Order.customer),
            )
            .where(
                Order.table_id == table_id,
                Order.status.notin_([OrderStatus.PAID, OrderStatus.CANCELLED]),
            )
            .order_by(Order.created_at.desc())
        )
        return result.scalars().first()

    async def get_kitchen_orders(self) -> Sequence[Order]:
        """Get orders that are in kitchen-relevant statuses."""
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product),
                selectinload(Order.table).selectinload(Table.floor),
            )
            .where(
                Order.status.in_([
                    OrderStatus.SENT_TO_KITCHEN,
                    OrderStatus.PREPARING,
                    OrderStatus.READY,
                ])
            )
            .order_by(Order.created_at.asc())
        )
        return result.scalars().all()

    async def get_kitchen_orders_simple(self) -> Sequence[Order]:
        """Get orders for KDS without complex nested loading."""
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product),
                selectinload(Order.table),
            )
            .where(
                Order.status.in_([
                    OrderStatus.SENT_TO_KITCHEN,
                    OrderStatus.PREPARING,
                    OrderStatus.READY,
                ])
            )
            .order_by(Order.created_at.asc())
        )
        return result.scalars().all()

    async def get_orders_by_session(self, session_id: int) -> Sequence[Order]:
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.session_id == session_id)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()

    async def get_next_order_number(self, session_id: int) -> str:
        """Generate sequential order number within session."""
        result = await self.db.execute(
            select(func.count(Order.id)).where(Order.session_id == session_id)
        )
        count = result.scalar() or 0
        return f"ORD-{session_id:04d}-{count + 1:04d}"

    async def search_orders(self, query: str) -> Sequence[Order]:
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product),
                selectinload(Order.table),
            )
            .where(Order.order_number.ilike(f"%{query}%"))
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()


class OrderItemRepository(BaseRepository[OrderItem]):
    def __init__(self, db: AsyncSession):
        super().__init__(OrderItem, db)

    async def get_items_by_order(self, order_id: int) -> Sequence[OrderItem]:
        result = await self.db.execute(
            select(OrderItem)
            .options(selectinload(OrderItem.product))
            .where(OrderItem.order_id == order_id)
        )
        return result.scalars().all()

    async def update_kitchen_status(
        self, item_id: int, status: KitchenStatus
    ) -> Optional[OrderItem]:
        item = await self.get_by_id(item_id)
        if item:
            item.kitchen_status = status
            await self.db.flush()
            await self.db.refresh(item)
        return item
