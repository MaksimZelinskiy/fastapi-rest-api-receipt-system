from databases import Database
from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import SQLAlchemyError
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db/receipts_db")

database = Database(DATABASE_URL)
metadata = MetaData()

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def connect_to_database():
    try:
        engine.connect()
        print("Database connection successful")
    except SQLAlchemyError as e:
        print(f"Database connection error: {e}")

async def close_database_connection():
    try:
        database.disconnect()
        print("Database connection closed")
    except SQLAlchemyError as e:
        print(f"Error closing database connection: {e}")

# Call the function to check the connection at the startup
connect_to_database()
