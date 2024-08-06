from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime
    

class ReceiptItem(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    total: float

    class Config:
        orm_mode = True

class Product(BaseModel):
    name: str
    price: float
    quantity: int

class Payment(BaseModel):
    type: Literal['cash', 'cashless']
    amount: float

class ReceiptCreate(BaseModel):
    products: List[Product]
    payment: Payment

class Receipt(BaseModel):
    id: int
    products: List[Product]
    payment: Payment
    total: float
    rest: float
    created_at: datetime