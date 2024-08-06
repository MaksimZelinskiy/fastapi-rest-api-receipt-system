from fastapi import FastAPI
from .routers import auth, receipts
from .database import database, metadata, engine, connect_to_database, close_database_connection
from .models import user, receipt

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Connect to the database
    await database.connect()
    connect_to_database()
    # Create all tables
    metadata.create_all(engine)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    await close_database_connection()

app.include_router(auth.router)
app.include_router(receipts.router)
