"""
Email Service — Mock implementation for sending receipts.
"""

import logging

logger = logging.getLogger("cafepos.email")


class EmailService:
    @staticmethod
    async def send_receipt_email(customer_email: str, order_number: str, pdf_bytes: bytes) -> bool:
        """
        Mock sending an email with a PDF attachment.
        In a production environment, this would integrate with SMTP or an API (e.g. SendGrid, SES).
        """
        logger.info(f"--- MOCK EMAIL DELIVERED ---")
        logger.info(f"To: {customer_email}")
        logger.info(f"Subject: Your Receipt for Order {order_number}")
        logger.info(f"Attachment: receipt_{order_number}.pdf ({len(pdf_bytes)} bytes)")
        logger.info(f"Message: Thank you for visiting Cafe POS!")
        logger.info(f"----------------------------")
        return True
