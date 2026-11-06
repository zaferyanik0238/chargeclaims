from sqlalchemy import Column, Integer, String
from database import Base

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    claim_id = Column(String, unique=True, index=True)
    order_id = Column(String)
    customer_name = Column(String)
    total_price = Column(String)
    created_at = Column(String)
    carrier = Column(String)
    tracking_number = Column(String)
    shipping_status = Column(String)
    delivery_address = Column(String)