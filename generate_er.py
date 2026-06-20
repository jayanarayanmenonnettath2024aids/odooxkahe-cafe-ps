import asyncio
from app.core.database import Base
from sqlalchemy.orm import class_mapper

def generate_mermaid():
    with open('er_diagram_utf8.txt', 'w', encoding='utf-8') as f:
        f.write("erDiagram\n")
        
        from app.models.category import Category
        from app.models.coupon import Coupon
        from app.models.customer import Customer
        from app.models.floor import Floor
        from app.models.order import Order, OrderItem
        from app.models.payment import Payment
        from app.models.payment_method import PaymentMethod
        from app.models.pos_session import PosSession
        from app.models.product import Product
        from app.models.promotion import Promotion
        from app.models.refresh_token import RefreshToken
        from app.models.reservation import Reservation
        from app.models.table import Table
        from app.models.user import User
        
        for table_name, table in Base.metadata.tables.items():
            f.write(f"    {table_name} {{\n")
            for col in table.columns:
                pk = "PK" if col.primary_key else ""
                fk = "FK" if col.foreign_keys else ""
                key_marker = pk or fk
                type_name = str(col.type).split("(")[0]
                f.write(f"        {type_name} {col.name} {key_marker}\n")
            f.write("    }\n")
            
            for col in table.columns:
                for fk in col.foreign_keys:
                    target_table = fk.target_fullname.split(".")[0]
                    f.write(f"    {table_name} }}|--|| {target_table} : \"{col.name}\"\n")

if __name__ == "__main__":
    generate_mermaid()
