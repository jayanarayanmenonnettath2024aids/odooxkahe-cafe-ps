"""
Payment service — cash, UPI, card payment processing.
"""

import io
import os
import uuid
from datetime import datetime, timezone

import qrcode
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException, PaymentException
from app.core.websocket_manager import WSEventType, ws_manager
from app.models.order import OrderStatus
from app.models.payment import PaymentStatus
from app.models.table import TableStatus
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_method_repository import PaymentMethodRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.table_repository import TableRepository
from app.schemas.payment import (
    CardPaymentRequest,
    CardPaymentResponse,
    CashPaymentRequest,
    CashPaymentResponse,
    UPIConfirmRequest,
    UPIPaymentRequest,
    UPIPaymentResponse,
)
from app.services.payment_method_service import PaymentMethodService


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.order_repo = OrderRepository(db)
        self.pm_repo = PaymentMethodRepository(db)
        self.table_repo = TableRepository(db)

    async def _validate_order_for_payment(self, order_id: int):
        order = await self.order_repo.get_full_order(order_id)
        if not order:
            raise NotFoundException("Order", order_id)
        if order.status == OrderStatus.PAID:
            raise BadRequestException("Order is already paid")
        return order

    async def process_cash_payment(self, data: CashPaymentRequest) -> CashPaymentResponse:
        """Process cash payment with change calculation."""
        order = await self._validate_order_for_payment(data.order_id)
        if order.status not in (OrderStatus.READY, OrderStatus.SENT_TO_KITCHEN, OrderStatus.PREPARING):
            raise BadRequestException(f"Cannot pay for order in status '{order.status.value}'")

        total = float(order.total_amount)
        if data.received_amount < total:
            raise PaymentException(
                f"Insufficient amount. Required: {total:.2f}, Received: {data.received_amount:.2f}"
            )

        change_due = round(data.received_amount - total, 2)

        # Find cash payment method
        cash_pm = await self.pm_repo.get_by_name("CASH")
        if not cash_pm:
            raise PaymentException("Cash payment method not configured")

        # Create payment record
        payment = await self.payment_repo.create({
            "order_id": data.order_id,
            "payment_method_id": cash_pm.id,
            "amount": total,
            "status": PaymentStatus.SUCCESS,
            "paid_at": datetime.now(timezone.utc),
        })

        # Mark order as paid
        await self._mark_order_paid(order)

        return CashPaymentResponse(
            order_id=data.order_id,
            total_amount=total,
            received_amount=data.received_amount,
            change_due=change_due,
            payment_status=PaymentStatus.SUCCESS,
        )

    async def process_upi_payment(self, data: UPIPaymentRequest) -> UPIPaymentResponse:
        """Generate UPI QR code for payment."""
        order = await self._validate_order_for_payment(data.order_id)

        total = float(order.total_amount)

        # Find UPI payment method
        upi_pm = await self.pm_repo.get_by_name("UPI")
        if not upi_pm:
            raise PaymentException("UPI payment method not configured")

        # Generate UPI payload
        pm_service = PaymentMethodService(self.db)
        upi_deeplink = pm_service.generate_upi_payload(upi_pm.upi_id or "cafepos@upi", total)

        # Generate QR image and save
        qr_filename = f"qr_{data.order_id}_{uuid.uuid4().hex[:8]}.png"
        qr_dir = os.path.join(os.getcwd(), "generated_qr")
        os.makedirs(qr_dir, exist_ok=True)
        qr_path = os.path.join(qr_dir, qr_filename)

        qr = qrcode.make(upi_deeplink)
        qr.save(qr_path)

        # Create pending payment record
        payment = await self.payment_repo.create({
            "order_id": data.order_id,
            "payment_method_id": upi_pm.id,
            "amount": total,
            "status": PaymentStatus.PENDING,
        })

        return UPIPaymentResponse(
            order_id=data.order_id,
            total_amount=total,
            qr_image_url=f"/static/qr/{qr_filename}",
            upi_deeplink=upi_deeplink,
            payment_id=payment.id,
        )

    async def confirm_upi_payment(self, data: UPIConfirmRequest) -> CashPaymentResponse:
        """Confirm a UPI payment after verification."""
        payment = await self.payment_repo.get_by_id(data.payment_id)
        if not payment:
            raise NotFoundException("Payment", data.payment_id)

        if payment.status == PaymentStatus.SUCCESS:
            raise BadRequestException("Payment is already successful")

        existing_txn = await self.payment_repo.get_by_transaction_reference(data.transaction_reference)
        if existing_txn and existing_txn.id != data.payment_id:
            raise BadRequestException("Transaction reference already used")

        payment.status = PaymentStatus.SUCCESS
        payment.transaction_reference = data.transaction_reference
        payment.paid_at = datetime.now(timezone.utc)
        await self.db.flush()

        order = await self.order_repo.get_full_order(payment.order_id)
        await self._mark_order_paid(order)

        return CashPaymentResponse(
            order_id=payment.order_id,
            total_amount=float(payment.amount),
            received_amount=float(payment.amount),
            change_due=0.0,
            payment_status=PaymentStatus.SUCCESS,
        )

    async def process_card_payment(self, data: CardPaymentRequest) -> CardPaymentResponse:
        """Process card payment."""
        order = await self._validate_order_for_payment(data.order_id)

        existing_txn = await self.payment_repo.get_by_transaction_reference(data.transaction_reference)
        if existing_txn:
            raise BadRequestException("Transaction reference already used")

        total = float(order.total_amount)

        card_pm = await self.pm_repo.get_by_name("CARD")
        if not card_pm:
            raise PaymentException("Card payment method not configured")

        payment = await self.payment_repo.create({
            "order_id": data.order_id,
            "payment_method_id": card_pm.id,
            "amount": total,
            "transaction_reference": data.transaction_reference,
            "status": PaymentStatus.SUCCESS,
            "paid_at": datetime.now(timezone.utc),
        })

        await self._mark_order_paid(order)

        return CardPaymentResponse(
            order_id=data.order_id,
            total_amount=total,
            transaction_reference=data.transaction_reference,
            payment_status=PaymentStatus.SUCCESS,
        )

    async def _mark_order_paid(self, order):
        """Mark order as paid, free table, and broadcast events."""
        order.status = OrderStatus.PAID
        await self.db.flush()

        # Free table
        await self.table_repo.update_status(order.table_id, TableStatus.AVAILABLE)

        # Broadcast payment success
        await ws_manager.broadcast_to_channel("pos", WSEventType.PAYMENT_SUCCESS, {
            "order_id": order.id,
            "order_number": order.order_number,
            "total_amount": float(order.total_amount),
        })

        await ws_manager.broadcast_to_channel(
            f"customer:{order.id}", WSEventType.CUSTOMER_DISPLAY_UPDATE,
            {"order_id": order.id, "status": "PAID"},
        )

        await ws_manager.broadcast_to_channel("tables", WSEventType.TABLE_STATUS_UPDATE, {
            "table_id": order.table_id,
            "status": "AVAILABLE",
        })
