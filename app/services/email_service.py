"""
Email Service — Mock implementation for sending receipts.
"""

import asyncio
import logging
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from app.core.config import get_settings
from app.core.templates import render_template

logger = logging.getLogger("cafepos.email")

class EmailService:
    @staticmethod
    def _dispatch_email(msg: MIMEMultipart, customer_email: str) -> bool:
        settings = get_settings()
        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
            logger.info(f"Email successfully sent to {customer_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {customer_email}: {e}")
            return False

    @staticmethod
    def _send_sync(customer_email: str, order_data: dict, pdf_bytes: bytes):
        settings = get_settings()
        if not settings.SMTP_HOST or not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            logger.warning("SMTP credentials not configured. Skipping email delivery.")
            return False

        order_number = order_data.get("order_number", "Unknown")

        msg = MIMEMultipart('alternative')
        msg["Subject"] = f"Your Receipt for Order {order_number}"
        msg["From"] = settings.EMAIL_FROM or settings.SMTP_USERNAME
        msg["To"] = customer_email
        
        # We now have the full order payload.
        # Pass it dynamically to the template.
        html_content = render_template("receipt_email.html", {
            "order_number": order_number,
            "date": order_data.get("created_at") or "Today",
            "items": order_data.get("items", []),
            "subtotal": order_data.get("subtotal", 0.0),
            "tax": order_data.get("tax_amount", 0.0),
            "discount": order_data.get("discount_amount", 0.0),
            "total": order_data.get("total_amount", 0.0),
            "payment_method": order_data.get("payment_method", "Cash/Card")
        })
        
        msg.attach(MIMEText("Thank you for visiting Cafe POS! Please find your receipt attached.", 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=f"receipt_{order_number}.pdf")
        msg.attach(pdf_attachment)

        return EmailService._dispatch_email(msg, customer_email)

    @staticmethod
    async def send_receipt_email(customer_email: str, order_data: dict, pdf_bytes: bytes) -> bool:
        """
        Sends an email with a PDF attachment via smtplib (non-blocking).
        """
        return await asyncio.to_thread(EmailService._send_sync, customer_email, order_data, pdf_bytes)

    @staticmethod
    def _send_res_sync(customer_email: str, reservation_id: int, date_str: str, time_str: str, guests: int):
        settings = get_settings()
        if not settings.SMTP_HOST or not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            logger.warning("SMTP credentials not configured. Skipping email delivery.")
            return False

        msg = MIMEMultipart('alternative')
        msg["Subject"] = f"Reservation Confirmation - {reservation_id}"
        msg["From"] = settings.EMAIL_FROM or settings.SMTP_USERNAME
        msg["To"] = customer_email
        
        html_content = render_template("reservation_confirmation.html", {
            "customer_name": "Valued Guest",
            "date": date_str,
            "time": time_str,
            "guest_count": guests,
            "table_number": "Assigned upon arrival",
            "reservation_id": reservation_id
        })
        
        text_content = f"Your reservation for {guests} guests on {date_str} at {time_str} is confirmed.\n\nThank you for choosing Cafe POS!"
        
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        return EmailService._dispatch_email(msg, customer_email)

    @staticmethod
    async def send_reservation_confirmation(customer_email: str, reservation_id: int, date_str: str, time_str: str, guests: int) -> bool:
        """
        Sends a reservation confirmation email (non-blocking).
        """
        return await asyncio.to_thread(EmailService._send_res_sync, customer_email, reservation_id, date_str, time_str, guests)
