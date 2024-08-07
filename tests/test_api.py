import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import database
import uuid


"""
=============================================================================== test session starts ===============================================================================
platform linux -- Python 3.9.19, pytest-8.3.2, pluggy-1.5.0 -- /usr/local/bin/python
cachedir: .pytest_cache
rootdir: /app
plugins: asyncio-0.23.8, anyio-4.4.0
asyncio: mode=strict
collected 6 items                                                                                                                                                                 

tests/test_api.py::test_registration PASSED                                                                                                                                 [ 16%]
tests/test_api.py::test_login PASSED                                                                                                                                        [ 33%]
tests/test_api.py::test_create_receipt PASSED                                                                                                                               [ 50%]
tests/test_api.py::test_get_receipts PASSED                                                                                                                                 [ 66%]
tests/test_api.py::test_public_receipt PASSED                                                                                                                               [ 83%]
tests/test_api.py::test_invalid_receipt_access PASSED                                                                                                                       [100%]

========================================================================= 6 passed, 15 warnings in 2.67s ==========================================================================
"""


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        database.connect()
        yield c
       
        # Очистка БД після завершення тесту
        database.execute("DELETE FROM users")
        database.execute("DELETE FROM receipts")
        database.execute("DELETE FROM receipt_items")
        
        database.disconnect()

def test_registration(client):
    # тест на реєстрації
    
    unique_username = f"testuser_{uuid.uuid4().hex}"
    response = client.post("/register", json={"name": "Test User", "username": unique_username, "password": "password"})
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data

def test_login(client):
    # тест на авторизації

    response = client.post("/token", data={"username": "testuser", "password": "password"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    return data["access_token"]

def test_create_receipt(client):
    # Тести створення чеків
    
    token = test_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    receipt_data = {
        "products": [
            {"name": "Product1", "price": 100.0, "quantity": 2},
            {"name": "Product2", "price": 50.0, "quantity": 1}
        ],
        "payment": {"type": "cash", "amount": 250.0}
    }
    response = client.post("/user/receipt", json=receipt_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["total"] == 250.0

def test_get_receipts(client):
    # Тести перегляду чеків
    
    token = test_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/user/receipts", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_public_receipt(client):
    # Тести публічного перегляду текстового представлення чеку
    
    # Створення чеку
    token = test_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    receipt_data = {
        "products": [
            {"name": "Product1", "price": 100.0, "quantity": 2},
            {"name": "Product2", "price": 50.0, "quantity": 1}
        ],
        "payment": {"type": "cash", "amount": 250.0}
    }
    response = client.post("/user/receipt", json=receipt_data, headers=headers)
    # пеервірка статусу
    assert response.status_code == 201
    receipt_id = response.json()["id"]
    # тест публічного просмотра чека
    response = client.get(f"/public/receipts/{receipt_id}")
    # пеервірка статусу
    assert response.status_code == 200
    # перевірка чи є ФОП в тексту
    assert "ФОП" in response.text

def test_invalid_receipt_access(client):
    # Тести недопустимих дій
    
    response = client.get("/public/receipts/999999")  # Перевірка ІД якого немає
    assert response.status_code == 404
    assert response.json()["detail"] == "Receipt not found"
