-- Очистка всех таблиц (с учётом связей)
TRUNCATE TABLE payments.payments CASCADE;
TRUNCATE TABLE orders.order_items CASCADE;
TRUNCATE TABLE orders.baskets CASCADE;
TRUNCATE TABLE orders.orders CASCADE;
TRUNCATE TABLE menu.combo_sets CASCADE;
TRUNCATE TABLE menu.dishes CASCADE;
TRUNCATE TABLE menu.categories CASCADE;
TRUNCATE TABLE menu.tags CASCADE;
TRUNCATE TABLE account.users CASCADE;

-- USERS (account.users)
INSERT INTO account.users (id, name, email, number_phone, hashed_password, is_admin, is_phone_verified, created_at, updated_at) VALUES
(1, 'Иван Иванов', 'ivan@example.com', '+79990000001', 'hash1', true, true, now(), now()),
(2, 'Петр Петров', 'petr@example.com', '+79990000002', 'hash2', false, true, now(), now()),
(3, 'Мария Смирнова', 'maria@example.com', '+79990000003', 'hash3', false, false, now(), now()),
(4, 'Анна Кузнецова', 'anna@example.com', '+79990000004', 'hash4', false, true, now(), now());

-- CATEGORIES (menu.categories)
INSERT INTO menu.categories (id, name, description) VALUES
(1, 'Супы', 'Горячие супы'),
(2, 'Салаты', 'Свежие салаты'),
(3, 'Горячее', 'Основные блюда'),
(4, 'Десерты', 'Сладкие блюда');

-- TAGS (menu.tags)
INSERT INTO menu.tags (id, name) VALUES
(1, 'Острое'),
(2, 'Вегетарианское'),
(3, 'Без глютена'),
(4, 'Детское');

-- DISHES (menu.dishes)
INSERT INTO menu.dishes (id, name, description, price, is_available, category_id) VALUES
(1, 'Борщ', 'Традиционный борщ', 250, true, 1),
(2, 'Оливье', 'Классический салат', 180, true, 2),
(3, 'Стейк', 'Говяжий стейк', 700, true, 3),
(4, 'Чизкейк', 'Нежный чизкейк', 300, true, 4);

-- COMBO_SETS (menu.combo_sets)
INSERT INTO menu.combo_sets (id, name, description, price) VALUES
(1, 'Обед №1', 'Суп + салат', 400),
(2, 'Детский сет', 'Салат + десерт', 350),
(3, 'Мясной сет', 'Стейк + гарнир', 800),
(4, 'Легкий сет', 'Салат + напиток', 250);

-- ORDERS (orders.orders)
INSERT INTO orders.orders (id, user_id, total_price, status, created_at, updated_at) VALUES
(1, 1, 430, 'PENDING', now(), now()),
(2, 2, 700, 'COMPLETED', now(), now()),
(3, 3, 300, 'PROCESSING', now(), now()),
(4, 4, 250, 'CANCELLED', now(), now());

-- BASKETS (orders.baskets)
INSERT INTO orders.baskets (id, user_id, item_id, quantity, price) VALUES
(1, 1, 1, 2, 500),
(2, 2, 2, 1, 180),
(3, 3, 3, 1, 700),
(4, 4, 4, 2, 600);

-- ORDER_ITEMS (orders.order_items)
INSERT INTO orders.order_items (id, order_id, dish_id, quantity, price) VALUES
(1, 1, 1, 1, 250),
(2, 1, 2, 1, 180),
(3, 2, 3, 1, 700),
(4, 3, 4, 1, 300);

-- PAYMENTS (payments.payments)
INSERT INTO payments.payments (id, invoice_id, amount, status, transaction_id, created_at, updated_at, order_id) VALUES
(1, 1, 430, 'pending', 'tx1', now(), now(), 1),
(2, 2, 700, 'completed', 'tx2', now(), now(), 2),
(3, 3, 300, 'completed', 'tx3', now(), now(), 3),
(4, 4, 250, 'cancelled', 'tx4', now(), now(), 4);
