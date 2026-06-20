"""
Retention Service — Automated cleanup and archiving.
"""

import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.payment import Payment
from app.models.reservation import Reservation

logger = logging.getLogger("cafepos.retention")

class RetentionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_retention_policy(self):
        """Run the retention policy across all configured tables."""
        now = datetime.now(timezone.utc)
        
        # Rule 1: Orders > 7 years (7 * 365 = 2555 days)
        cutoff_7_years = now - timedelta(days=2555)
        
        # Rule 2: Reservations > 2 years (2 * 365 = 730 days)
        cutoff_2_years = now - timedelta(days=730)

        # In a real enterprise system, we would move these to archive tables or rely on Snapshots.
        # Since we have Snapshots (Feature 2) and Analytics Mirrors (Feature 3), we can safely hard-delete 
        # or soft-delete the hot transactional tables to save space. We will hard delete here as they are archived.
        
        # 1. Cleanup Old Orders
        # Order deletion cascades to order_items, order_versions, payments via foreign keys if configured correctly.
        try:
            res1 = await self.db.execute(
                delete(Order).where(Order.created_at < cutoff_7_years)
            )
            logger.info(f"Retention: Deleted {res1.rowcount} orders older than 7 years.")
            
            # 2. Cleanup Old Reservations
            res2 = await self.db.execute(
                delete(Reservation).where(Reservation.created_at < cutoff_2_years)
            )
            logger.info(f"Retention: Deleted {res2.rowcount} reservations older than 2 years.")
            
            # 3. Cleanup Old Payments (In case of detached payments)
            res3 = await self.db.execute(
                delete(Payment).where(Payment.created_at < cutoff_7_years)
            )
            logger.info(f"Retention: Deleted {res3.rowcount} detached payments older than 7 years.")

            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Retention policy execution failed: {e}")
            raise
