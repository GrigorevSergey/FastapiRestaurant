# Примеры API запросов для тестирования

## Переменные окружения

```bash
export BASE_URL="http://localhost"
export USER_SERVICE="$BASE_URL:8000"
export MENU_SERVICE="$BASE_URL:8001"
export ORDER_SERVICE="$BASE_URL:8003"
export PAYMENT_SERVICE="$BASE_URL:8004"
export TOKEN="your_jwt_token_here"
```

## 1. Управление пользователями

### Регистрация
```bash
curl -X POST "$USER_SERVICE/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

### Авторизация
```bash
curl -X POST "$USER_SERVICE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpassword123"
  }'
```

### Получение информации о пользователе
```bash
curl -X GET "$USER_SERVICE/users/me" \
  -H "Authorization: Bearer $TOKEN"
```

## 2. Работа с меню

### Получение всех блюд
```bash
curl -X GET "$MENU_SERVICE/dishes" \
  -H "Authorization: Bearer $TOKEN"
```

### Получение конкретного блюда
```bash
curl -X GET "$MENU_SERVICE/dishes/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Создание нового блюда (если есть права)
```bash
curl -X POST "$MENU_SERVICE/dishes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Тестовое блюдо",
    "description": "Описание тестового блюда",
    "price": 50000,
    "category": "Основные блюда",
    "is_available": true
  }'
```

## 3. Управление корзиной

### Добавление товара в корзину
```bash
curl -X POST "$ORDER_SERVICE/order/baskets?dish_id=1&quantity=2" \
  -H "Authorization: Bearer $TOKEN"
```

### Просмотр корзины
```bash
curl -X GET "$ORDER_SERVICE/order/baskets" \
  -H "Authorization: Bearer $TOKEN"
```

### Обновление количества в корзине
```bash
curl -X PUT "$ORDER_SERVICE/order/baskets/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 3
  }'
```

### Удаление товара из корзины
```bash
curl -X DELETE "$ORDER_SERVICE/order/baskets/1" \
  -H "Authorization: Bearer $TOKEN"
```

## 4. Управление заказами

### Создание заказа из корзины
```bash
curl -X POST "$ORDER_SERVICE/order/baskets/bask-to-order" \
  -H "Authorization: Bearer $TOKEN"
```

### Получение всех заказов
```bash
curl -X GET "$ORDER_SERVICE/order/orders" \
  -H "Authorization: Bearer $TOKEN"
```

### Получение конкретного заказа
```bash
curl -X GET "$ORDER_SERVICE/order/orders/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Обновление заказа
```bash
curl -X PUT "$ORDER_SERVICE/order/orders/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "total_price": 150000,
    "status": "CONFIRMED",
    "updated_at": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'"
  }'
```

### Получение информации о платеже для заказа
```bash
curl -X GET "$ORDER_SERVICE/order/orders/1/payment" \
  -H "Authorization: Bearer $TOKEN"
```

## 5. Управление платежами

### Создание платежа
```bash
curl -X POST "$PAYMENT_SERVICE/payments/create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_id": 1,
    "amount": 150000
  }'
```

### Получение платежа по ID
```bash
curl -X GET "$PAYMENT_SERVICE/payments/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Получение платежа по ID заказа
```bash
curl -X GET "$PAYMENT_SERVICE/payments/order/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Обновление статуса платежа
```bash
curl -X PUT "$PAYMENT_SERVICE/payments/1/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "COMPLETED",
    "transaction_id": "test_txn_123"
  }'
```

## 6. Webhook симуляции

### Успешный платеж
```bash
curl -X POST "$PAYMENT_SERVICE/payments/webhook/cloudpayments" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "test_txn_1_1234",
    "amount": 150000,
    "status": "success",
    "order_id": 1,
    "invoice_id": 1
  }'
```

### Отклоненный платеж
```bash
curl -X POST "$PAYMENT_SERVICE/payments/webhook/cloudpayments" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "test_txn_1_1234",
    "amount": 150000,
    "status": "failed",
    "order_id": 1,
    "invoice_id": 1
  }'
```

### Отмененный платеж
```bash
curl -X POST "$PAYMENT_SERVICE/payments/webhook/cloudpayments" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "test_txn_1_1234",
    "amount": 150000,
    "status": "cancelled",
    "order_id": 1,
    "invoice_id": 1
  }'
```

## 7. Health checks

### Проверка всех сервисов
```bash
echo "=== Health Checks ==="
curl -s "$USER_SERVICE/health" | jq
curl -s "$MENU_SERVICE/health" | jq
curl -s "$ORDER_SERVICE/health" | jq
curl -s "$PAYMENT_SERVICE/health" | jq
```

## 8. Полный сценарий в одном скрипте

```bash
#!/bin/bash

# Настройка переменных
BASE_URL="http://localhost"
USER_SERVICE="$BASE_URL:8000"
MENU_SERVICE="$BASE_URL:8001"
ORDER_SERVICE="$BASE_URL:8003"
PAYMENT_SERVICE="$BASE_URL:8004"

# Регистрация и авторизация
TIMESTAMP=$(date +%s)
USERNAME="testuser_$TIMESTAMP"
EMAIL="test$TIMESTAMP@example.com"

echo "Регистрация пользователя..."
curl -X POST "$USER_SERVICE/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"email\": \"$EMAIL\", \"password\": \"testpassword123\"}"

echo -e "\nАвторизация..."
LOGIN_RESPONSE=$(curl -s -X POST "$USER_SERVICE/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"testpassword123\"}")

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo "Токен получен: ${TOKEN:0:20}..."

# Добавление в корзину
echo -e "\nДобавление товара в корзину..."
curl -X POST "$ORDER_SERVICE/order/baskets?dish_id=1&quantity=2" \
  -H "Authorization: Bearer $TOKEN"

# Создание заказа
echo -e "\nСоздание заказа..."
ORDER_RESPONSE=$(curl -s -X POST "$ORDER_SERVICE/order/baskets/bask-to-order" \
  -H "Authorization: Bearer $TOKEN")

ORDER_ID=$(echo $ORDER_RESPONSE | jq -r '.id')
TOTAL_PRICE=$(echo $ORDER_RESPONSE | jq -r '.total_price')

echo "Заказ создан: ID=$ORDER_ID, Сумма=$TOTAL_PRICE"

# Симуляция оплаты
echo -e "\nСимуляция успешной оплаты..."
curl -X POST "$PAYMENT_SERVICE/payments/webhook/cloudpayments" \
  -H "Content-Type: application/json" \
  -d "{\"transaction_id\": \"test_txn_${ORDER_ID}_1234\", \"amount\": $TOTAL_PRICE, \"status\": \"success\", \"order_id\": $ORDER_ID, \"invoice_id\": $ORDER_ID}"

# Проверка результата
echo -e "\nПроверка статуса платежа..."
curl -X GET "$PAYMENT_SERVICE/payments/order/$ORDER_ID" \
  -H "Authorization: Bearer $TOKEN" | jq

echo -e "\nТестирование завершено!"
```

## 9. Отладка и мониторинг

### Просмотр логов Docker
```bash
# Логи конкретного сервиса
docker-compose logs -f order-service
docker-compose logs -f payment-service

# Логи всех сервисов
docker-compose logs -f

# Последние 100 строк логов
docker-compose logs --tail=100 order-service
```

### Проверка состояния контейнеров
```bash
docker-compose ps
docker-compose top
```

### Подключение к базе данных
```bash
docker exec -it postgresapp_fastapi psql -U projectuser -d fast

# В psql:
\dt orders.*     # Таблицы заказов
\dt payments.*   # Таблицы платежей

SELECT * FROM orders.orders ORDER BY created_at DESC LIMIT 5;
SELECT * FROM payments.payments ORDER BY created_at DESC LIMIT 5;
```

### Мониторинг RabbitMQ
- Веб-интерфейс: http://localhost:15672
- Логин/пароль: guest/guest

### Мониторинг Redis
- Redis Commander: http://localhost:8081

## 10. Статусы и коды ответов

### Статусы заказов
- `PENDING` - В ожидании
- `CONFIRMED` - Подтвержден
- `PREPARING` - Готовится
- `READY` - Готов
- `DELIVERED` - Доставлен
- `CANCELLED` - Отменен

### Статусы платежей
- `PENDING` - В ожидании
- `COMPLETED` - Завершен
- `FAILED` - Неудачный
- `CANCELLED` - Отменен

### HTTP коды ответов
- `200` - Успешно
- `201` - Создано
- `204` - Удалено
- `400` - Неверный запрос
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Не найдено
- `422` - Ошибка валидации
- `500` - Внутренняя ошибка сервера