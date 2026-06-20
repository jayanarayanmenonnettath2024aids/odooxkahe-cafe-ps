"""
Unit tests for business logic — coupon validation, promotion engine, order state machine.
"""

from datetime import date, timedelta

import pytest

from app.models.coupon import Coupon, DiscountType
from app.models.order import ORDER_TRANSITIONS, OrderStatus
from app.models.promotion import Promotion, PromotionDiscountType, PromotionScope
from app.services.coupon_service import CouponService
from app.services.promotion_service import PromotionService


class TestCouponValidation:
    """Test coupon discount calculation."""

    def test_percentage_discount(self):
        coupon = Coupon(
            id=1, code="TEST10", discount_type=DiscountType.PERCENTAGE,
            discount_value=10, is_active=True,
        )
        discount = CouponService.calculate_discount(coupon, 1000)
        assert discount == 100.0

    def test_fixed_discount(self):
        coupon = Coupon(
            id=1, code="FLAT50", discount_type=DiscountType.FIXED,
            discount_value=50, is_active=True,
        )
        discount = CouponService.calculate_discount(coupon, 1000)
        assert discount == 50.0

    def test_fixed_discount_caps_at_order_total(self):
        coupon = Coupon(
            id=1, code="FLAT200", discount_type=DiscountType.FIXED,
            discount_value=200, is_active=True,
        )
        discount = CouponService.calculate_discount(coupon, 100)
        assert discount == 100.0  # Capped at order total

    def test_percentage_discount_on_zero(self):
        coupon = Coupon(
            id=1, code="TEST10", discount_type=DiscountType.PERCENTAGE,
            discount_value=10, is_active=True,
        )
        discount = CouponService.calculate_discount(coupon, 0)
        assert discount == 0.0


class TestPromotionEngine:
    """Test promotion discount calculation."""

    def test_order_level_percentage_discount(self):
        promo = Promotion(
            id=1, name="Test", promotion_scope=PromotionScope.ORDER,
            discount_type=PromotionDiscountType.PERCENTAGE,
            discount_value=15, minimum_order_amount=500, is_active=True,
        )
        discount = PromotionService.calculate_promotion_discount(promo, 1000, 3)
        assert discount == 150.0

    def test_order_below_minimum_returns_zero(self):
        promo = Promotion(
            id=1, name="Test", promotion_scope=PromotionScope.ORDER,
            discount_type=PromotionDiscountType.PERCENTAGE,
            discount_value=15, minimum_order_amount=500, is_active=True,
        )
        discount = PromotionService.calculate_promotion_discount(promo, 300, 2)
        assert discount == 0.0

    def test_product_level_quantity_check(self):
        promo = Promotion(
            id=1, name="Buy 3 Test", promotion_scope=PromotionScope.PRODUCT,
            discount_type=PromotionDiscountType.FIXED,
            discount_value=50, minimum_quantity=3, is_active=True,
        )
        # Meets minimum
        discount = PromotionService.calculate_promotion_discount(promo, 500, 3)
        assert discount == 50.0

        # Below minimum
        discount = PromotionService.calculate_promotion_discount(promo, 500, 2)
        assert discount == 0.0

    def test_fixed_discount_caps_at_total(self):
        promo = Promotion(
            id=1, name="Test", promotion_scope=PromotionScope.ORDER,
            discount_type=PromotionDiscountType.FIXED,
            discount_value=500, is_active=True,
        )
        discount = PromotionService.calculate_promotion_discount(promo, 200, 1)
        assert discount == 200.0


class TestOrderStateMachine:
    """Test order state transition rules."""

    def test_valid_transitions(self):
        assert OrderStatus.SENT_TO_KITCHEN in ORDER_TRANSITIONS[OrderStatus.DRAFT]
        assert OrderStatus.CANCELLED in ORDER_TRANSITIONS[OrderStatus.DRAFT]
        assert OrderStatus.PREPARING in ORDER_TRANSITIONS[OrderStatus.SENT_TO_KITCHEN]
        assert OrderStatus.READY in ORDER_TRANSITIONS[OrderStatus.PREPARING]
        assert OrderStatus.PAID in ORDER_TRANSITIONS[OrderStatus.READY]

    def test_invalid_transitions(self):
        assert OrderStatus.PAID not in ORDER_TRANSITIONS[OrderStatus.DRAFT]
        assert OrderStatus.READY not in ORDER_TRANSITIONS[OrderStatus.DRAFT]
        assert len(ORDER_TRANSITIONS[OrderStatus.PAID]) == 0
        assert len(ORDER_TRANSITIONS[OrderStatus.CANCELLED]) == 0

    def test_all_statuses_have_transitions(self):
        for status in OrderStatus:
            assert status in ORDER_TRANSITIONS
