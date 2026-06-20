"""
Report schemas.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ReportFilters(BaseModel):
    period: Optional[str] = None  # "today", "week", "month", "custom"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    employee_id: Optional[int] = None
    session_id: Optional[int] = None
    product_id: Optional[int] = None


class TopProductReport(BaseModel):
    product_id: int
    product_name: str
    quantity_sold: int
    revenue: float


class TopCategoryReport(BaseModel):
    category_id: int
    category_name: str
    quantity_sold: int
    revenue: float


class SalesTrendPoint(BaseModel):
    date: str
    orders: int
    revenue: float


class DashboardResponse(BaseModel):
    total_orders: int = 0
    total_revenue: float = 0.0
    average_order_value: float = 0.0
    top_products: list[TopProductReport] = []
    top_categories: list[TopCategoryReport] = []
    sales_trend: list[SalesTrendPoint] = []


class ExportRequest(BaseModel):
    format: str = "pdf"  # "pdf" or "xlsx"
    filters: Optional[ReportFilters] = None
