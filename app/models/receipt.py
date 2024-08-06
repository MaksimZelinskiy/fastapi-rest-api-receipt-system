from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime, MetaData, Float
from ..database import metadata
from datetime import datetime

receipts = Table(
    "receipts",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("total", Float),
    Column("payment_type", String),
    Column("payment_amount", Float),
    Column("rest", Float),
)

receipt_items = Table(
    "receipt_items",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("receipt_id", Integer, ForeignKey("receipts.id")),
    Column("name", String, nullable=False),
    Column("price", Float, nullable=False),
    Column("quantity", Float, nullable=False),
    Column("total", Float),
)
