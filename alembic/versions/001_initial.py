"""Initial migration — all tables

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("ADMIN", "EMPLOYEE", name="userrole"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # Customers
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_customers_email", "customers", ["email"])
    op.create_index("ix_customers_phone", "customers", ["phone"])

    # Categories
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("color", sa.String(7), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Products
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("tax_percentage", sa.Numeric(5, 2), server_default="0"),
        sa.Column("unit_of_measure", sa.String(20), nullable=True, server_default="unit"),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_name", "products", ["name"])

    # Floors
    op.create_table(
        "floors",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Tables
    op.create_table(
        "tables",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("floor_id", sa.Integer(), sa.ForeignKey("floors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("table_number", sa.String(20), nullable=False),
        sa.Column("seat_count", sa.Integer(), server_default="4"),
        sa.Column("active_status", sa.Enum("AVAILABLE", "OCCUPIED", "RESERVED", name="tablestatus"), server_default="AVAILABLE"),
        sa.Column("unique_token", sa.String(36), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("unique_token"),
    )
    op.create_index("ix_tables_unique_token", "tables", ["unique_token"])

    # Payment Methods
    op.create_table(
        "payment_methods",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true"),
        sa.Column("upi_id", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Coupons
    op.create_table(
        "coupons",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("discount_type", sa.Enum("PERCENTAGE", "FIXED", name="discounttype"), nullable=False),
        sa.Column("discount_value", sa.Numeric(10, 2), nullable=False),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_coupons_code", "coupons", ["code"])

    # Promotions
    op.create_table(
        "promotions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("promotion_scope", sa.Enum("PRODUCT", "ORDER", name="promotionscope"), nullable=False),
        sa.Column("minimum_quantity", sa.Integer(), nullable=True),
        sa.Column("minimum_order_amount", sa.Numeric(10, 2), nullable=True),
        sa.Column("discount_type", sa.Enum("PERCENTAGE", "FIXED", name="promotiondiscounttype"), nullable=False),
        sa.Column("discount_value", sa.Numeric(10, 2), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.PrimaryKeyConstraint("id"),
    )

    # POS Sessions
    op.create_table(
        "pos_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("opened_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("opening_balance", sa.Numeric(10, 2), server_default="0"),
        sa.Column("closing_balance", sa.Numeric(10, 2), nullable=True),
        sa.Column("status", sa.Enum("OPEN", "CLOSED", name="sessionstatus"), server_default="OPEN"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Orders
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_number", sa.String(20), nullable=False),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("pos_sessions.id"), nullable=False),
        sa.Column("table_id", sa.Integer(), sa.ForeignKey("tables.id"), nullable=False),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.Enum("DRAFT", "SENT_TO_KITCHEN", "PREPARING", "READY", "PAID", "CANCELLED", name="orderstatus"), server_default="DRAFT"),
        sa.Column("subtotal", sa.Numeric(10, 2), server_default="0"),
        sa.Column("tax_amount", sa.Numeric(10, 2), server_default="0"),
        sa.Column("discount_amount", sa.Numeric(10, 2), server_default="0"),
        sa.Column("total_amount", sa.Numeric(10, 2), server_default="0"),
        sa.Column("coupon_id", sa.Integer(), sa.ForeignKey("coupons.id", ondelete="SET NULL"), nullable=True),
        sa.Column("promotion_id", sa.Integer(), sa.ForeignKey("promotions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_number"),
    )
    op.create_index("ix_orders_order_number", "orders", ["order_number"])
    op.create_index("ix_orders_status", "orders", ["status"])

    # Order Items
    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default="1"),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("tax_amount", sa.Numeric(10, 2), server_default="0"),
        sa.Column("discount_amount", sa.Numeric(10, 2), server_default="0"),
        sa.Column("line_total", sa.Numeric(10, 2), server_default="0"),
        sa.Column("kitchen_status", sa.Enum("TO_COOK", "PREPARING", "COMPLETED", name="kitchenstatus"), server_default="TO_COOK"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Payments
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("payment_method_id", sa.Integer(), sa.ForeignKey("payment_methods.id"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("transaction_reference", sa.String(255), nullable=True),
        sa.Column("status", sa.Enum("PENDING", "SUCCESS", "FAILED", name="paymentstatus"), server_default="PENDING"),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("payments")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("pos_sessions")
    op.drop_table("promotions")
    op.drop_table("coupons")
    op.drop_table("payment_methods")
    op.drop_table("tables")
    op.drop_table("floors")
    op.drop_table("products")
    op.drop_table("categories")
    op.drop_table("customers")
    op.drop_table("users")
