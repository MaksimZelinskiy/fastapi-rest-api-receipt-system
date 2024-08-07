# Тестове завдання для Python Backend Developer

Метою цього проєкту є розробка REST API для створення та перегляду чеків з реєстрацією та авторизацією користувачів.

### Функціонал

1. **Реєстрація користувача**
    - Користувачі можуть зареєструватись, надавши обов'язкові дані, такі як ім'я, логін та пароль.
    - Ендпоінт: `/register`
    
2. **Авторизація користувача**
    - Користувачі можуть увійти в систему, використовуючи свій логін та пароль, щоб отримати унікальний JWT токен для доступу до API.
    - Ендпоінт: `/token`

3. **Створення чеків продажу**
    - Авторизовані користувачі можуть створювати чеки продажу, що містять інформацію про товари, їх кількість, ціну та додаткові опції.
    - Чек включає ідентифікатор, дату створення та користувача, який його створив.
    - Ендпоінт: `/user/receipt`

4. **Перегляд та фільтрація чеків**
    - Авторизовані користувачі можуть переглядати список своїх чеків з можливістю фільтрації за різними параметрами, такими як дата створення, загальна сума та тип оплати.
    - Ендпоінт: `/user/receipts`

5. **Публічний перегляд чеків**
    - Кожен чек має посилання, що дозволяє неавторизованим користувачам переглядати чек у текстовому форматі.
    - Ендпоінт: `/public/receipts/{receipt_id}`

### Технічні вимоги

- **Мова програмування**: Python
- **Веб-фреймворк**: FastAPI, aiohttp або BackSheep
- **База даних**: PostgreSQL
- **Документація API**: Вбудована документація FastAPI за адресою `/docs`
- **Тестування**: pytest для перевірки функціональності

## Структура проєкту

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── security.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── receipt.py
│   │   ├── user.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── receipts.py
│   │   ├── auth.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── receipt.py
│   │   ├── user.py
│   ├── config
│   │   ├── dictionaries.py
├── tests/
│   ├── __init__.py
│   ├── test_api.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Ендпоінти API

### Реєстрація користувача
- **Ендпоінт**: `/register`
- **Метод**: POST
- **Тіло запиту**:
  ```json
  {
    "name": "string",
    "username": "string",
    "password": "string"
  }
  ```
- **Відповідь**:
  ```json
  {
    "access_token": "string",
    "token_type": "bearer"
  }
  ```

### Логін користувача
- **Ендпоінт**: `/token`
- **Метод**: POST
- **Тіло запиту**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Відповідь**:
  ```json
  {
    "access_token": "string",
    "token_type": "bearer"
  }
  ```

### Створення чеку
- **Ендпоінт**: `/user/receipt`
- **Метод**: POST
- **Тіло запиту**:
  ```json
  {
    "products": [
      {
        "name": "string",
        "price": "decimal",
        "quantity": "int"
      }
    ],
    "payment": {
      "type": "cash" or "cashless",
      "amount": "decimal"
    }
  }
  ```
- **Відповідь**:
  ```json
  {
    "id": "int",
    "products": [
      {
        "name": "string",
        "price": "decimal",
        "quantity": "int",
        "total": "decimal"
      }
    ],
    "payment": {
      "type": "cash" or "cashless",
      "amount": "decimal"
    },
    "total": "decimal",
    "rest": "decimal",
    "created_at": "datetime"
  }
  ```

### Перегляд чеків
- **Ендпоінт**: `/user/receipts`
- **Метод**: GET
- **Параметри**:
  - `skip`: int (за замовчуванням: 0)
  - `limit`: int (за замовчуванням: 10)
  - `start_date`: "datetime"
  - `end_date`: "datetime"
  - `min_total`: "float"
  - `max_total`: "float"
  - `payment_type`: "string"
- **Відповідь**:
  ```json
  [
    {
      "id": "int",
      "products": [
        {
          "name": "string",
          "price": "decimal",
          "quantity": "int",
          "total": "decimal"
        }
      ],
      "payment": {
        "type": "cash" or "cashless",
        "amount": "decimal"
      },
      "total": "decimal",
      "rest": "decimal",
      "created_at": "datetime"
    }
  ]
  ```

### Публічний перегляд чеку
- **Ендпоінт**: `/public/receipts/{receipt_id}`
- **Метод**: GET
- **Параметри**:
  - `receipt_id`: int (path)
  - `char_per_line`: int (query, 40 по стандарту)
- **Відповідь**:
  
![Снимок экрана](https://github.com/user-attachments/assets/897dfaef-d465-41ac-ae6a-fbcd5eb6fd36)


## Налаштування та встановлення

### Встановлення

1. Клонування репозиторію:
   ```bash
   git clone https://github.com/MaksimZelinskiy/fastapi-rest-api-receipt-system.git
   cd fastapi-rest-api-receipt-system/
   ```

2. Побудова та запуск Docker контейнерів:
   ```bash
   docker-compose up --build
   ```

3. API буде доступний за адресою `http://localhost:8000`.

### Запуск тестів

1. Запуск тестів за допомогою Docker:
   ```bash
   docker-compose run test
   ```

### Документація API
- Документація API доступна за адресою `http://localhost:8000/docs`.

## Тестування

### Сценарії тестування

- **Реєстрація та авторизація користувачів**:
  - Переконатись, що користувачі можуть успішно реєструватись, авторизуватись та отримувати токени для доступу до API.
- **Створення чеків**:
  - Перевірити, чи можуть користувачі створювати нові чеки та отримувати підтвердження про успішне створення.
- **Перегляд чеків**:
  - Переконатись, що користувачі можуть переглядати свої чеки та використовувати параметри пагінації та фільтрації.
- **Публічний перегляд чеків**:
  - Перевірити, чи може будь-хто, знаючи ID чеку, переглянути чек у текстовому вигляді.
- **Некоректні дії**:
  - Переконатись, що API правильно обробляє некоректні запити
