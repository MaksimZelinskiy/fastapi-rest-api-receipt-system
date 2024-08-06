from fastapi import APIRouter, Depends, HTTPException, status, Query
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse

from typing import List, Optional
from datetime import datetime, timedelta
from ..schemas import receipt as schemas_receipt
from ..schemas import user as schemas_user
from ..models import receipt as models_receipt
from ..models import user as models_users
from ..core.auth import get_current_user
from ..database import database
from ..config import dictionaries
from sqlalchemy import and_, or_

import locale 

router = APIRouter()


@router.post("/user/receipt", response_model=schemas_receipt.Receipt)
async def create_receipt(receipt: schemas_receipt.ReceiptCreate, current_user: schemas_user.User = Depends(get_current_user)):
    """ 
    Створення нового чека.

    Цей ендпоінт дозволяє створити новий чек, надавши деталі продуктів та інформацію про оплату.

    - **ReceiptCreate**:
        - **products**: Список продуктів у чеку:
            - **name**: Назва продукту.
            - **price**: Ціна продукту.
            - **quantity**: Кількість.
        - **payment**: Інформація про оплату:
            - **type**: Тип оплати (наприклад, "cash" або "cashless").
            - **amount**: Сума оплати.
    - **current_user**: авторизований користувач.
    - **return**: Створений чек. 
    """

    # Загальна сума чека
    sum_price = sum(item.price * item.quantity for item in receipt.products)
    query = models_receipt.receipts.insert().values(
        user_id=current_user.id,
        created_at=datetime.utcnow(),
        total=sum_price,
        payment_type=receipt.payment.type,
        payment_amount=receipt.payment.amount,
        rest=receipt.payment.amount - sum_price
    )
    last_record_id = await database.execute(query)
    
    products_response = []
    for item in receipt.products:
        item_query = models_receipt.receipt_items.insert().values(
            receipt_id=last_record_id,
            name=item.name,
            price=item.price,
            quantity=item.quantity,
            total=item.price * item.quantity
        )
        item_id = await database.execute(item_query)
        products_response.append({
            "id": item_id,
            "name": item.name,
            "price": item.price,
            "quantity": item.quantity,
            "total": item.price * item.quantity
        })
    
    response = {
        "id": last_record_id,
        "user_id": current_user.id,
        "products": products_response,
        "payment_type": receipt.payment.type,
        "payment_amount": receipt.payment.amount,
        "payment": {
            "type": receipt.payment.type,
            "amount": receipt.payment.amount
        },
        "total": sum_price,
        "rest": receipt.payment.amount - sum_price,
        "created_at": datetime.utcnow().isoformat() 
    }
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=response)




@router.get("/user/receipts", response_model=List[schemas_receipt.Receipt])
async def get_receipts(
    skip: int = 0, 
    limit: int = 10, 
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    min_total: Optional[float] = Query(None),
    max_total: Optional[float] = Query(None),
    payment_type: Optional[str] = Query(None),
    current_user: schemas_user.User = Depends(get_current_user)
):
    """
    Перегляд та фільтрація списку власних чеків.

    Цей ендпоінт дозволяє переглянути та відфільтрувати список власних чеків за такими параметрами:
    - **skip**: Пропустити перші {N} записів.
    - **limit**: Максимальна кількість записів.
    - **start_date**: Дата початку для фільтрації.
    - **end_date**: Дата закінчення для фільтрації.
    - **min_total**: Мінімальна сума чека для фільтрації.
    - **max_total**: Максимальна сума чека для фільтрації.
    - **payment_type**: Тип оплати для фільтрації.
    - **current_user**: Поточний авторизований користувач.
    - **return**: Список чеків, що відповідають умовам фільтрації.
    """

    filters = [models_receipt.receipts.c.user_id == current_user.id]

    if start_date is not None:
        filters.append(models_receipt.receipts.c.created_at >= start_date)
    if end_date is not None:
        filters.append(models_receipt.receipts.c.created_at <= end_date)
    if min_total is not None:
        filters.append(models_receipt.receipts.c.total >= min_total)
    if max_total is not None:
        filters.append(models_receipt.receipts.c.total <= max_total)
    if payment_type is not None:
        filters.append(models_receipt.receipts.c.payment_type == payment_type)

    query = models_receipt.receipts.select().where(and_(*filters)).offset(skip).limit(limit)
    receipts = await database.fetch_all(query)
    
    receipts_response = []
    for receipt in receipts:
        products_query = models_receipt.receipt_items.select().where(models_receipt.receipt_items.c.receipt_id == receipt.id)
        products = await database.fetch_all(products_query)
        
        products_response = [
            {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": product.quantity,
                "total": product.total
            }
            for product in products
        ]

        receipts_response.append({
            "id": receipt.id,
            "products": products_response,
            "payment": {
                "type": receipt.payment_type,
                "amount": receipt.payment_amount
            },
            "total": receipt.total,
            "rest": receipt.rest,
            "created_at": receipt.created_at.isoformat()
        })
    
    
    return receipts_response



@router.get("/public/receipts/{receipt_id}")
async def get_public_receipt(request: Request, receipt_id: int, char_per_line: int = Query(40, alias="charPerLine")):
    """
    Отримання публічного чека за його ID.

    - **receipt_id**: ID чека.
    - **char_per_line**: Кількість символів у рядку для форматування чека.
    - **return**: Відформатований публічний чек у вигляді тексту.
    """
    
    # Запит на пошук чека
    query = models_receipt.receipts.select().where(models_receipt.receipts.c.id == receipt_id)
    receipt = await database.fetch_one(query)
    
    if receipt is None:
        raise HTTPException(status_code=404, detail="Receipt not found")

    query = models_users.users.select().where(models_users.users.c.id == receipt['user_id'])
    user = await database.fetch_one(query)
    
    items_query = models_receipt.receipt_items.select().where(models_receipt.receipt_items.c.receipt_id == receipt_id)
    items = await database.fetch_all(items_query)
    
    formatted_receipt = format_receipt(receipt, items, user, char_per_line)
    
    return PlainTextResponse(formatted_receipt)


# Функція для форматування текста для вивода чека
def format_receipt(receipt, items: List[dict], user, line_width: int) -> str:
    """
    Функція для форматування чека для відображення.

    - **receipt**: Дані чека.
    - **items**: Продукти, що входять до чека.
    - **user**: Користувач, що створив чек.
    - **line_width**: Кількість символів у рядку.
    - **return**: Відформатований чек у вигляді тексту.
    """
    
    def format_line(left: str, right: str, width: int) -> str:
        """Форматує рядок з текстом зліва та справа."""
        left_width = width - len(right) - 1
        return f"{left:<{left_width}} {right}"
    
    def format_currency(value: float) -> str:
        """Форматує число з роздільниками тисяч. 2000 -> 2 000"""
        return locale.format_string("%0.2f", value, grouping=True)

    # Заголовок чека
    header = f"ФОП {user['name']}".center(line_width)
    separator = "=" * line_width
    lines = [header, separator]
    
    # створення продуктів чеека
    for index, item in enumerate(items):
        quantity_price = f"{item['quantity']} x {format_currency(item['price'])}".ljust(line_width)
        name = item['name']
        lines.append(quantity_price)
        lines.append(name.ljust(line_width-10) + f"{format_currency(item['total'])}".rjust(10))
        if index < len(items) - 1:
            lines.append('-' * line_width)

    lines.append(separator)
    
    # Отрименя типу оплати (формутування в потрібний вигляд)
    payment_type = dictionaries.payment_types.get(receipt['payment_type'], 'НЕВІДОМИЙ ТИП ОПЛАТИ') # cash -> Готівка

    # Форматування чека (суми + дата)
    total_line = format_line("СУМА", format_currency(receipt['total']), line_width)
    payment_line = format_line(payment_type, format_currency(receipt['payment_amount']), line_width)
    rest_line = format_line("Решта", format_currency(receipt['rest']), line_width)
    date_line = receipt['created_at'].strftime("%d.%m.%Y %H:%M").center(line_width)
    thank_you_line = "Дякуємо за покупку!".center(line_width)

    lines.extend([total_line, payment_line, rest_line, separator, date_line, thank_you_line])
    return "\n".join(lines)

