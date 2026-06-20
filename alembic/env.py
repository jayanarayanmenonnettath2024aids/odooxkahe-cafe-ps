"""
Alembic environment configuration.
Imports all models so autogenerate can detect them.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import get_settings
from app.core.database import Base

# Import ALL models so Alembic sees them
from app.models.user import User  # noqa
from app.models.customer import Customer  # noqa
from app.models.category import Category  # noqa
from app.models.product import Product  # noqa
from app.models.floor import Floor  # noqa
from app.models.table import Table  # noqa
from app.models.payment_method import PaymentMethod  # noqa
from app.models.coupon import Coupon  # noqa
from app.models.promotion import Promotion  # noqa
from app.models.pos_session import PosSession  # noqa
from app.models.order import Order, OrderItem  # noqa
from app.models.payment import Payment  # noqa
from app.models.reservation import Reservation  # noqa
from app.models.refresh_token import RefreshToken  # noqa
from app.models.snapshot import OrderSnapshot, PaymentSnapshot, ReservationSnapshot, DailySalesSnapshot  # noqa
from app.models.order_version import OrderVersion  # noqa
from app.models.analytics_mirror import OrdersAnalytics, PaymentsAnalytics, ReservationsAnalytics, CustomerAnalytics  # noqa
from app.models.store_setting import StoreSetting  # noqa

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.sync_database_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
