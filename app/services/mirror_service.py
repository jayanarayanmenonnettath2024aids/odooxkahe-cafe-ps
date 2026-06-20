"""
Analytics Mirror Service — Synchronizes live transactional data to the Data Warehouse mirror.
"""

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.analytics_mirror import OrdersAnalytics


class MirrorService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def sync_order(self, order_id: int):
        """Sync a single order to the analytics mirror."""
        # This would typically be triggered out-of-band (e.g., via background task)
        order = await self.db.get(Order, order_id)
        if not order:
            return

        existing_result = await self.db.execute(
            select(OrdersAnalytics).where(OrdersAnalytics.original_order_id == order_id)
        )
        existing = existing_result.scalar_one_or_none()

        payload = {
            "order_number": order.order_number,
            "status": order.status.value,
            "order_type": order.order_type.value,
            "subtotal": float(order.subtotal),
            "tax_amount": float(order.tax_amount),
            "discount_amount": float(order.discount_amount),
            "total_amount": float(order.total_amount),
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat()
        }

        if existing:
            existing.payload = payload
            existing.synced_at = datetime.now(timezone.utc)
        else:
            mirror = OrdersAnalytics(
                original_order_id=order_id,
                payload=payload
            )
            self.db.add(mirror)
            
        await self.db.commit()
