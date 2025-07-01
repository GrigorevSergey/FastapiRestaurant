-- Заполняем тестовыми данными

-- Добавляем тестовых пользователей
INSERT INTO account.users (name, email, number_phone, hashed_password, is_admin, is_phone_verified, created_at)
VALUES 
    ('Admin User', 'admin@example.com', '+79001234567', 'hashed_password', true, true, NOW()),
    ('Regular User', 'user@example.com', '+79007654321', 'hashed_password', false, true, NOW());

-- Добавляем категории меню
INSERT INTO menu.categories (name, description, created_at)
VALUES 
    ('Main Dishes', 'Основные блюда', NOW()),
    ('Drinks', 'Напитки', NOW()),
    ('Desserts', 'Десерты', NOW());

-- Добавляем теги
INSERT INTO menu.tags (name, created_at)
VALUES 
    ('Vegetarian', NOW()),
    ('Spicy', NOW()),
    ('Healthy', NOW());

-- Добавляем блюда
INSERT INTO menu.dishes (name, description, price, is_available, category_id, created_at)
VALUES 
    ('Pizza Margherita', 'Классическая пицца с томатами и моцареллой', 1000, true, 1, NOW()),
    ('Pasta Carbonara', 'Паста с беконом и пармезаном', 1200, true, 1, NOW()),
    ('Cola', 'Кока-кола 0.5л', 100, true, 2, NOW()),
    ('Ice Cream', 'Ванильное мороженое', 200, true, 3, NOW());

-- Связываем блюда с тегами
INSERT INTO menu.dish_tags (dish_id, tag_id)
VALUES 
    (1, 1),  -- Pizza Margherita - Vegetarian
    (1, 2),  -- Pizza Margherita - Spicy
    (2, 1),  -- Pasta Carbonara - Vegetarian
    (3, 3),  -- Cola - Healthy
    (4, 1);  -- Ice Cream - Vegetarian

-- Создаем тестовый заказ
WITH order_data AS (
    INSERT INTO orders.orders (user_id, total_price, status, created_at, updated_at)
    VALUES (2, 1300, 'pending', NOW(), NOW())
    RETURNING id
)
INSERT INTO orders.order_items (order_id, dish_id, quantity, price, created_at)
SELECT 
    o.id,
    d.id,
    CASE WHEN d.id = 1 THEN 1 ELSE 2 END,
    d.price,
    NOW()
FROM order_data o
CROSS JOIN (
    SELECT id, price FROM menu.dishes WHERE id IN (1, 3)
) d;

-- Создаем транзакцию для заказа
INSERT INTO payments.payments (invoice_id, amount, status, created_at, updated_at)
SELECT 
    o.id,
    o.total_price,
    'PENDING',
    NOW(),
    NOW()
FROM orders.orders o
WHERE o.id = (SELECT id FROM orders.orders ORDER BY id DESC LIMIT 1);
