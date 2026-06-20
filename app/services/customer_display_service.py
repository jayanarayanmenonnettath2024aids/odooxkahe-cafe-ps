"""
Customer Display service — real-time order view for customer-facing screens.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.order_repository import OrderRepository
from app.schemas.customer_display import (
    CustomerDisplayItemResponse,
    CustomerDisplayResponse,
)


class CustomerDisplayService:
    def __init__(self, db: AsyncSession):
        self.order_repo = OrderRepository(db)

    async def get_display(self, order_id: int) -> CustomerDisplayResponse:
        """Get customer-facing display data for an order."""
        order = await self.order_repo.get_full_order(order_id)
        if not order:
            raise NotFoundException("Order", order_id)

        return CustomerDisplayResponse(
            order_id=order.id,
            order_number=order.order_number,
            items=[
                CustomerDisplayItemResponse(
                    product_name=item.product.name if item.product else "Unknown",
                    quantity=item.quantity,
                    unit_price=float(item.unit_price),
                    line_total=float(item.line_total),
                )
                for item in order.items
            ],
            subtotal=float(order.subtotal),
            tax_amount=float(order.tax_amount),
            discount_amount=float(order.discount_amount),
            total_amount=float(order.total_amount),
            payment_status=order.status,
            table_number=order.table.table_number if order.table else None,
        )
