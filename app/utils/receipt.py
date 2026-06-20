"""
Receipt generation utility using ReportLab.
"""

import io
from datetime import datetime

from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors


def generate_receipt_pdf(order_data: dict) -> bytes:
    """
    Generate a PDF receipt for an order.

    order_data expected keys:
      - order_number, table_number, employee_name
      - items: [{product_name, quantity, unit_price, line_total}]
      - subtotal, tax_amount, discount_amount, total_amount
      - payment_method, paid_at
    """
    buffer = io.BytesIO()

    # Receipt paper: 80mm width
    page_width = 80 * mm
    page_height = 200 * mm  # Adjustable

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(page_width, page_height),
        leftMargin=5 * mm,
        rightMargin=5 * mm,
        topMargin=5 * mm,
        bottomMargin=5 * mm,
    )

    styles = getSampleStyleSheet()
    center_style = ParagraphStyle("center", parent=styles["Normal"], alignment=1, fontSize=8)
    bold_center = ParagraphStyle("bold_center", parent=styles["Normal"], alignment=1, fontSize=10, fontName="Helvetica-Bold")
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=7)

    from typing import Any
    elements: list[Any] = []

    # Header
    elements.append(Paragraph("☕ CAFE POS", bold_center))
    elements.append(Spacer(1, 3 * mm))
    elements.append(Paragraph(f"Order: {order_data.get('order_number', '')}", center_style))
    elements.append(Paragraph(f"Table: {order_data.get('table_number', '-')}", center_style))
    elements.append(Paragraph(f"Staff: {order_data.get('employee_name', '-')}", center_style))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", center_style))
    elements.append(Spacer(1, 3 * mm))
    elements.append(Paragraph("─" * 40, center_style))

    # Items
    items = order_data.get("items", [])
    table_data = [["Item", "Qty", "Price", "Total"]]
    for item in items:
        table_data.append([
            item.get("product_name", "")[:20],
            str(item.get("quantity", 0)),
            f"₹{item.get('unit_price', 0):.0f}",
            f"₹{item.get('line_total', 0):.0f}",
        ])

    if table_data:
        t = Table(table_data, colWidths=[25 * mm, 10 * mm, 15 * mm, 15 * mm])
        t.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
            ("TOPPADDING", (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ]))
        elements.append(t)

    elements.append(Paragraph("─" * 40, center_style))

    # Totals
    subtotal = order_data.get("subtotal", 0)
    tax = order_data.get("tax_amount", 0)
    discount = order_data.get("discount_amount", 0)
    total = order_data.get("total_amount", 0)

    totals_data = [
        ["Subtotal:", f"₹{subtotal:.2f}"],
        ["Tax:", f"₹{tax:.2f}"],
    ]
    if discount > 0:
        totals_data.append(["Discount:", f"-₹{discount:.2f}"])
    totals_data.append(["TOTAL:", f"₹{total:.2f}"])

    t2 = Table(totals_data, colWidths=[35 * mm, 30 * mm])
    t2.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ]))
    elements.append(t2)

    elements.append(Spacer(1, 3 * mm))
    elements.append(Paragraph(f"Payment: {order_data.get('payment_method', 'N/A')}", center_style))
    elements.append(Spacer(1, 3 * mm))
    elements.append(Paragraph("Thank you for dining with us!", center_style))
    elements.append(Paragraph("☕ ❤️", center_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
