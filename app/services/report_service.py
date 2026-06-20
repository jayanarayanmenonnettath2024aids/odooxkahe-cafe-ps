"""
Report service — dashboard metrics, sales trends, and export.
"""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select, cast, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.category import Category
from app.schemas.report import (
    DashboardResponse,
    ReportFilters,
    SalesTrendPoint,
    TopCategoryReport,
    TopProductReport,
)


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard(self, filters: ReportFilters) -> DashboardResponse:
        """Generate dashboard metrics with filters."""
        start_date, end_date = self._resolve_date_range(filters)

        # Base query for paid orders
        base_filter = [Order.status == OrderStatus.PAID]
        if start_date:
            base_filter.append(Order.created_at >= datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc))
        if end_date:
            base_filter.append(Order.created_at <= datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc))
        if filters.employee_id:
            base_filter.append(Order.employee_id == filters.employee_id)
        if filters.session_id:
            base_filter.append(Order.session_id == filters.session_id)

        # Total orders & revenue
        result = await self.db.execute(
            select(
                func.count(Order.id),
                func.coalesce(func.sum(Order.total_amount), 0),
            ).where(*base_filter)
        )
        row = result.one()
        total_orders = row[0] or 0
        total_revenue = float(row[1] or 0)
        avg_order_value = round(total_revenue / total_orders, 2) if total_orders > 0 else 0

        # Top products
        top_products_query = (
            select(
                Product.id,
                Product.name,
                func.sum(OrderItem.quantity).label("qty"),
                func.sum(OrderItem.line_total).label("rev"),
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, Order.id == OrderItem.order_id)
            .where(*base_filter)
            .group_by(Product.id, Product.name)
            .order_by(func.sum(OrderItem.line_total).desc())
            .limit(10)
        )
        result = await self.db.execute(top_products_query)
        top_products = [
            TopProductReport(
                product_id=row[0],
                product_name=row[1],
                quantity_sold=int(row[2]),
                revenue=float(row[3]),
            )
            for row in result.all()
        ]

        # Top categories
        top_categories_query = (
            select(
                Category.id,
                Category.name,
                func.sum(OrderItem.quantity).label("qty"),
                func.sum(OrderItem.line_total).label("rev"),
            )
            .join(Product, Product.category_id == Category.id)
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, Order.id == OrderItem.order_id)
            .where(*base_filter)
            .group_by(Category.id, Category.name)
            .order_by(func.sum(OrderItem.line_total).desc())
            .limit(10)
        )
        result = await self.db.execute(top_categories_query)
        top_categories = [
            TopCategoryReport(
                category_id=row[0],
                category_name=row[1],
                quantity_sold=int(row[2]),
                revenue=float(row[3]),
            )
            for row in result.all()
        ]

        # Sales trend (daily)
        trend_query = (
            select(
                func.substr(cast(Order.created_at, String), 1, 10).label("day"),
                func.count(Order.id),
                func.coalesce(func.sum(Order.total_amount), 0),
            )
            .where(*base_filter)
            .group_by("day")
            .order_by("day")
        )
        result = await self.db.execute(trend_query)
        sales_trend = [
            SalesTrendPoint(
                date=str(row[0]) if row[0] else "",
                orders=int(row[1]),
                revenue=float(row[2]),
            )
            for row in result.all()
        ]

        return DashboardResponse(
            total_orders=total_orders,
            total_revenue=total_revenue,
            average_order_value=avg_order_value,
            top_products=top_products,
            top_categories=top_categories,
            sales_trend=sales_trend,
        )

    def _resolve_date_range(self, filters: ReportFilters) -> tuple[date | None, date | None]:
        """Resolve period string to date range."""
        today = date.today()

        if filters.period == "today":
            return today, today
        elif filters.period == "week":
            return today - timedelta(days=7), today
        elif filters.period == "month":
            return today - timedelta(days=30), today
        elif filters.period == "custom":
            return filters.start_date, filters.end_date
        else:
            return filters.start_date, filters.end_date
