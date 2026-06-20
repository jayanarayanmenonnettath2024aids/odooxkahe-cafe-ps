"""
QR code generation utility.
"""

import io
import os
import uuid

import qrcode
from qrcode.constants import ERROR_CORRECT_M


def _create_qr(data: str) -> qrcode.QRCode:
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr

def generate_qr_code(data: str, filename: str | None = None) -> str:
    """
    Generate a QR code image and save it.
    Returns the relative URL path to the QR image.
    """
    qr = _create_qr(data)
    img = qr.make_image(fill_color="black", back_color="white")

    if not filename:
        filename = f"qr_{uuid.uuid4().hex[:8]}.png"

    qr_dir = os.path.join(os.getcwd(), "generated_qr")
    os.makedirs(qr_dir, exist_ok=True)
    filepath = os.path.join(qr_dir, filename)

    img.save(filepath)
    return f"/static/qr/{filename}"


def generate_qr_bytes(data: str) -> bytes:
    """Generate a QR code and return as bytes."""
    qr = _create_qr(data)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
