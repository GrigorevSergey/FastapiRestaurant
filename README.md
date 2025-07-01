# Restaurantflow — Документация по REST API

## Сервисы и порты

| Сервис           | Название контейнера | Порт (host:container) | Назначение                |
|------------------|--------------------|----------------------|---------------------------|
| Users Service    | users-service      | 8000:8000            | Аутентификация, пользователи |
| Menu Service     | menu-service       | 8001:8001            | Меню, категории, блюда    |
| Some Service     | some-service       | 8002:8002            | (доп. сервис, пример)     |
| Order Service    | order-service      | 8003:8003            | Заказы, корзины           |
| Payment Service  | payment-service    | 8004:8004            | Платежи                   |
| RabbitMQ         | rabbitmq           | 5672:5672, 15672:15672| Очереди сообщений         |
| Postgres         | postgresapp_fastapi| 5432:5432            | База данных               |
| Redis            | redis              | 6379:6379            | Кэш                       |
| Redis Commander  | redis-commander    | 8081:8081            | Веб-интерфейс Redis       |

---

## Аутентификация и пользователи

### Регистрация (отправка SMS)
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"number_phone": "+79001234567"}'
```

### Подтверждение кода (получение токена)
```bash
curl -X POST http://localhost:8000/auth/confirm \
  -H "Content-Type: application/json" \
  -d '{"number_phone": "+79001234567", "code": "1234"}'
```

### Вход (логин)
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"number_phone": "+79001234567", "password": "your_password"}'
```

### Проверка токена (для микросервисов)
```bash
curl -X GET http://localhost:8000/auth/verify \
  -H "Authorization: Bearer <TOKEN>"
```

### Получить/обновить профиль пользователя
```bash
curl -X GET http://localhost:8000/users/ \
  -H "Authorization: Bearer <TOKEN>"

curl -X PUT http://localhost:8000/users/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Name"}'
```

### Получить пользователя по id (только для админа)
```bash
curl -X GET http://localhost:8000/users/<user_id> \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

---

## Меню (Menu Service)

### Получить список категорий
```bash
curl http://localhost:8001/menu/categories
```

### Получить категорию по id
```bash
curl http://localhost:8001/menu/categories/1
```

### Создать категорию (только админ)
```bash
curl -X POST http://localhost:8001/menu/categories \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Пицца", "description": "Пиццы и фокачча"}'
```

### Обновить категорию (только админ)
```bash
curl -X PUT http://localhost:8001/menu/categories/1 \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Пицца NEW", "description": "Обновлено"}'
```

### Удалить категорию (только админ)
```bash
curl -X DELETE http://localhost:8001/menu/categories/1 \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

### Получить блюда
```bash
curl http://localhost:8001/menu/dishes
```

### Получить блюда по категории
```bash
curl http://localhost:8001/menu/dishes/1
```

### Получить блюдо по id
```bash
curl http://localhost:8001/dishes/1
```

### Создать блюдо (только админ)
```bash
curl -X POST http://localhost:8001/menu/dishes \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Пицца Маргарита", "description": "Классика", "price": 1000, "category_id": 1}'
```

### Обновить блюдо (только админ)
```bash
curl -X PUT http://localhost:8001/menu/dishes/1 \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Пицца Маргарита NEW", "description": "Обновлено", "price": 1100, "category_id": 1}'
```

### Удалить блюдо (только админ)
```bash
curl -X DELETE http://localhost:8001/menu/dishes/1 \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

### Получить теги
```bash
curl http://localhost:8001/menu/tags
```

### Создать тег (только админ)
```bash
curl -X POST http://localhost:8001/menu/tags \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Вегетарианское"}'
```

---

## Заказы (Order Service)

### Получить список заказов
```bash
curl http://localhost:8002/order/orders
```

### Получить заказ по id
```bash
curl http://localhost:8002/order/orders/1
```

### Создать заказ
```bash
curl -X POST http://localhost:8002/order/orders \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"dish_id": 1, "quantity": 2}]}'
```

### Обновить заказ
```bash
curl -X PUT http://localhost:8002/order/orders/1 \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

### Удалить заказ
```bash
curl -X DELETE http://localhost:8002/order/orders/1 \
  -H "Authorization: Bearer <TOKEN>"
```

### Получить корзины
```bash
curl http://localhost:8002/order/baskets
```

### Добавить в корзину
```bash
curl -X POST http://localhost:8002/order/baskets \
  -H "Authorization: Bearer <TOKEN>" \
  -d 'dish_id=1&quantity=2'
```

---

## Платежи (Payment Service)

### Создать платеж
```bash
curl -X POST http://localhost:8004/payments/create \
  -H "Content-Type: application/json" \
  -d '{"invoice_id": 1, "amount": 1300}'
```

### Получить платеж по id
```bash
curl http://localhost:8004/payments/1
```

### Получить платеж по заказу
```bash
curl http://localhost:8004/payments/order/1
```

### Обновить статус платежа (админ/система)
```bash
curl -X PUT http://localhost:8004/payments/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "COMPLETED", "transaction_id": "abc-123"}'
```

### Webhook CloudPayments (для теста)
```bash
curl -X POST http://localhost:8004/payments/webhook/cloudpayments \
  -H "Content-Type: application/json" \
  -d '{"order_id": 1, "transaction_id": "test-123", "status": "success", "amount": 1300}'
```

---

## Примечания
- Все ручки, требующие авторизации, требуют заголовок `Authorization: Bearer <TOKEN>`.
- Для админских ручек используйте токен администратора.
- Порты сервисов могут отличаться в вашей docker-compose.
- Для подробной OpenAPI-спеки используйте `/docs` у каждого микросервиса.
