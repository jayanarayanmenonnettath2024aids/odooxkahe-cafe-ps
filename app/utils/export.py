"""
Report export utilities — PDF and XLSX.
"""

import io
from typing import Any

import openpyxl
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def export_dashboard_xlsx(dashboard_data: dict) -> bytes:
    """Export dashboard data as XLSX."""
    wb = openpyxl.Workbook()

    ws = wb.active
    if ws is not None:
        ws.title = "Summary"
        ws.append(["Metric", "Value"])
        ws.append(["Total Orders", dashboard_data.get("total_orders", 0)])
        ws.append(["Total Revenue", dashboard_data.get("total_revenue", 0)])
        ws.append(["Average Order Value", dashboard_data.get("average_order_value", 0)])

    # Top Products
    ws2 = wb.create_sheet("Top Products")
    ws2.append(["Product", "Quantity Sold", "Revenue"])
    for p in dashboard_data.get("top_products", []):
        ws2.append([p.get("product_name", ""), p.get("quantity_sold", 0), p.get("revenue", 0)])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def export_dashboard_pdf(dashboard_data: dict) -> bytes:
    """Export dashboard data as PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements: list[Any] = []

    elements.append(Paragraph("CafePOS Sales Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    data = [
        ["Metric", "Value"],
        ["Total Orders", str(dashboard_data.get("total_orders", 0))],
        ["Total Revenue", f"₹{dashboard_data.get('total_revenue', 0):.2f}"],
        ["Avg Order Value", f"₹{dashboard_data.get('average_order_value', 0):.2f}"],
    ]

    t = Table(data, colWidths=[200, 200])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#714B67")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
