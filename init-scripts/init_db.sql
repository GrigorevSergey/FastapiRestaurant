-- Удаляем существующие схемы
DROP SCHEMA IF EXISTS public CASCADE;
DROP SCHEMA IF EXISTS account CASCADE;
DROP SCHEMA IF EXISTS menu CASCADE;
DROP SCHEMA IF EXISTS orders CASCADE;
DROP SCHEMA IF EXISTS payments CASCADE;

-- Создаем новые схемы
CREATE SCHEMA account;
CREATE SCHEMA menu;
CREATE SCHEMA orders;
CREATE SCHEMA payments;
CREATE SCHEMA public;

-- Создаем таблицу пользователей в схеме account
CREATE TABLE account.users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    number_phone VARCHAR(20) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_phone_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Создаем таблицы меню в схеме menu
CREATE TABLE menu.categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE menu.tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE menu.dishes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price INTEGER NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    category_id INTEGER REFERENCES menu.categories(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE menu.dish_tags (
    dish_id INTEGER REFERENCES menu.dishes(id),
    tag_id INTEGER REFERENCES menu.tags(id),
    PRIMARY KEY (dish_id, tag_id)
);

-- Создаем таблицы заказов в схеме orders
CREATE TYPE orders.order_status AS ENUM ('pending', 'processing', 'completed', 'cancelled');

CREATE TABLE orders.orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES account.users(id),
    total_price INTEGER NOT NULL,
    status orders.order_status NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE orders.baskets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES account.users(id),
    item_id INTEGER REFERENCES menu.dishes(id),
    quantity INTEGER NOT NULL,
    price INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders.order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders.orders(id),
    dish_id INTEGER REFERENCES menu.dishes(id),
    quantity INTEGER NOT NULL,
    price INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создаем тип ENUM для статуса платежа
CREATE TYPE payments.paymentstatus AS ENUM ('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED');

-- Создаем таблицы платежей в схеме payments
CREATE TABLE payments.payments (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES orders.orders(id),
    amount INTEGER NOT NULL,
    status payments.paymentstatus NOT NULL,
    transaction_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Добавляем индексы для оптимизации
CREATE INDEX idx_users_email ON account.users(email);
CREATE INDEX idx_users_phone ON account.users(number_phone);
CREATE INDEX idx_dishes_category ON menu.dishes(category_id);
CREATE INDEX idx_orders_user ON orders.orders(user_id);
CREATE INDEX idx_order_items_order ON orders.order_items(order_id);
CREATE INDEX idx_payments_invoice ON payments.payments(invoice_id);
