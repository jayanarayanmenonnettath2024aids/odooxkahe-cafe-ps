"""
Receipt generation utility using ReportLab.
"""

import io
from datetime import datetime

from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors


import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image
from app.utils.qr import generate_qr_bytes

def _register_fonts():
    font_path = r"C:\Windows\Fonts\arial.ttf"
    bold_font_path = r"C:\Windows\Fonts\arialbd.ttf"
    if os.path.exists(font_path) and os.path.exists(bold_font_path):
        try:
            pdfmetrics.registerFont(TTFont('Unicode', font_path))
            pdfmetrics.registerFont(TTFont('Unicode-Bold', bold_font_path))
            return 'Unicode', 'Unicode-Bold'
        except Exception:
            pass
    return 'Helvetica', 'Helvetica-Bold'


def generate_receipt_pdf(order_data: dict) -> bytes:
    """
    Generate a professional PDF receipt for an order.
    """
    buffer = io.BytesIO()

    # Receipt paper: 80mm width
    page_width = 80 * mm
    page_height = 250 * mm  # Long enough for items + QR

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(page_width, page_height),
        leftMargin=5 * mm,
        rightMargin=5 * mm,
        topMargin=5 * mm,
        bottomMargin=5 * mm,
    )

    base_font, bold_font = _register_fonts()

    styles = getSampleStyleSheet()
    center_style = ParagraphStyle("center", parent=styles["Normal"], alignment=1, fontSize=8, fontName=base_font)
    bold_center = ParagraphStyle("bold_center", parent=styles["Normal"], alignment=1, fontSize=12, fontName=bold_font)
    small_center = ParagraphStyle("small_center", parent=styles["Normal"], alignment=1, fontSize=7, fontName=base_font)
    left_style = ParagraphStyle("left", parent=styles["Normal"], alignment=0, fontSize=8, fontName=base_font)

    from typing import Any
    elements: list[Any] = []

    # --- Header ---
    elements.append(Paragraph("<b>CAFE POS</b>", bold_center))
    elements.append(Paragraph("123 Coffee Street, Tech Hub", small_center))
    elements.append(Paragraph("Tel: +1 234 567 8900", small_center))
    elements.append(Spacer(1, 4 * mm))
    
    # --- Metadata ---
    meta_data = [
        ["Order No:", order_data.get('order_number', '')],
        ["Date:", order_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M'))],
        ["Type:", order_data.get('order_type', 'DINE_IN').replace('_', ' ')],
    ]
    if order_data.get('table_number'):
        meta_data.append(["Table:", str(order_data.get('table_number'))])
    if order_data.get('customer_name'):
        meta_data.append(["Customer:", order_data.get('customer_name')])
    if order_data.get('employee_name'):
        meta_data.append(["Served By:", order_data.get('employee_name')])

    meta_t = Table(meta_data, colWidths=[20 * mm, 50 * mm])
    meta_t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (-1, -1), base_font),
        ("FONTNAME", (0, 0), (0, -1), bold_font),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    elements.append(meta_t)
    elements.append(Spacer(1, 3 * mm))
    elements.append(Paragraph("─" * 45, center_style))

    # --- Items ---
    items = order_data.get("items", [])
    table_data = [["Item", "Qty", "Price", "Total"]]
    for item in items:
        table_data.append([
            item.get("product_name", "")[:18],
            str(item.get("quantity", 0)),
            f"₹{item.get('unit_price', 0):.0f}",
            f"₹{item.get('line_total', 0):.0f}",
        ])

    if table_data:
        t = Table(table_data, colWidths=[30 * mm, 10 * mm, 15 * mm, 15 * mm])
        t.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("FONTNAME", (0, 0), (-1, -1), base_font),
            ("FONTNAME", (0, 0), (-1, 0), bold_font),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
            ("TOPPADDING", (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ]))
        elements.append(t)

    elements.append(Paragraph("─" * 45, center_style))

    # --- Totals ---
    subtotal = float(order_data.get("subtotal", 0) or 0)
    tax = float(order_data.get("tax_amount", 0) or 0)
    discount = float(order_data.get("discount_amount", 0) or 0)
    total = float(order_data.get("total_amount", 0) or 0)

    totals_data = [
        ["Subtotal:", f"₹{subtotal:.2f}"],
        ["Tax:", f"₹{tax:.2f}"],
    ]
    if order_data.get("coupon_id"):
        totals_data.append(["Coupon Applied:", f"#{order_data.get('coupon_id')}"])
    if discount > 0:
        totals_data.append(["Discount:", f"-₹{discount:.2f}"])
    totals_data.append(["TOTAL:", f"₹{total:.2f}"])

    t2 = Table(totals_data, colWidths=[35 * mm, 35 * mm])
    t2.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (-1, -1), base_font),
        ("FONTNAME", (0, -1), (-1, -1), bold_font),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
    ]))
    elements.append(t2)

    elements.append(Spacer(1, 3 * mm))
    elements.append(Paragraph(f"Payment: {order_data.get('payment_method', 'N/A')}", center_style))
    elements.append(Spacer(1, 5 * mm))

    # --- QR Code ---
    try:
        tracking_url = f"https://cafepos.app/track/{order_data.get('id')}"
        qr_bytes = generate_qr_bytes(tracking_url)
        qr_img = Image(io.BytesIO(qr_bytes), width=30*mm, height=30*mm)
        elements.append(qr_img)
        elements.append(Spacer(1, 2 * mm))
        elements.append(Paragraph("Scan to track your order", small_center))
    except Exception as e:
        pass

    # --- Footer ---
    elements.append(Spacer(1, 5 * mm))
    elements.append(Paragraph("<b>Thank you for your visit!</b>", center_style))
    elements.append(Paragraph("Please visit again", small_center))
    elements.append(Spacer(1, 2 * mm))
    elements.append(Paragraph("Support: support@cafepos.app | +1 234 567 8900", small_center))
    elements.append(Paragraph(f"Receipt ID: {order_data.get('id', '-')}", small_center))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
