from sqlalchemy import Table, Column, Integer, String, MetaData
from ..database import metadata

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("username", String, nullable=False, unique=True),
    Column("hashed_password", String, nullable=False),
)
