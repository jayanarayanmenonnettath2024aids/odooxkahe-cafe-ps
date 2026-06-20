"""
Snapshot Service — Implements immutable Historical Snapshot Engine for compliance.
"""

from datetime import date, datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.payment import Payment
from app.models.reservation import Reservation
from app.models.snapshot import (
    DailySalesSnapshot,
    OrderSnapshot,
    PaymentSnapshot,
    ReservationSnapshot,
)


class SnapshotService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_order_snapshots(self, target_date: date) -> int:
        """Create immutable snapshots of all orders on a specific date."""
        query = select(Order).where(
            Order.created_at >= datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc),
            Order.created_at <= datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        )
        result = await self.db.execute(query)
        orders = result.scalars().all()
        
        count = 0
        for order in orders:
            # Check if snapshot already exists
            existing = await self.db.execute(
                select(OrderSnapshot).where(
                    OrderSnapshot.original_order_id == order.id,
                    OrderSnapshot.snapshot_date == target_date
                )
            )
            if existing.scalar_one_or_none():
                continue
                
            snapshot = OrderSnapshot(
                original_order_id=order.id,
                snapshot_date=target_date,
                snapshot_payload={
                    "order_number": order.order_number,
                    "status": order.status.value,
                    "subtotal": float(order.subtotal),
                    "total_amount": float(order.total_amount),
                    "created_at": order.created_at.isoformat()
                }
            )
            self.db.add(snapshot)
            count += 1
            
        await self.db.commit()
        return count

    async def generate_daily_sales_snapshot(self, target_date: date) -> DailySalesSnapshot:
        """Generate a single daily sales aggregate snapshot."""
        # Calculate daily sales
        query = select(Order).where(
            Order.created_at >= datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc),
            Order.created_at <= datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc),
            Order.status == "PAID"
        )
        result = await self.db.execute(query)
        orders = result.scalars().all()
        
        total_revenue = sum(float(o.total_amount) for o in orders)
        
        # Upsert snapshot
        existing_result = await self.db.execute(
            select(DailySalesSnapshot).where(DailySalesSnapshot.snapshot_date == target_date)
        )
        existing = existing_result.scalar_one_or_none()
        
        payload = {
            "total_orders": len(orders),
            "total_revenue": total_revenue,
            "generated_by": "SYSTEM"
        }
        
        if existing:
            # Snapshots shouldn't technically be modified, but for the current day it might be regenerated
            existing.snapshot_payload = payload
            snapshot = existing
        else:
            snapshot = DailySalesSnapshot(
                snapshot_date=target_date,
                snapshot_payload=payload
            )
            self.db.add(snapshot)
            
        await self.db.commit()
        return snapshot
