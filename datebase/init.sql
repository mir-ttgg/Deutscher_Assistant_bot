-- 1️⃣ Создание роли (пользователя)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_roles WHERE rolname = 'deutscher_assistant'
    ) THEN
        CREATE ROLE deutscher_assistant
        WITH LOGIN
        PASSWORD 'your_password';
        
        RAISE NOTICE '✅ Роль deutscher_assistant создана';
    ELSE
        RAISE NOTICE 'ℹ️ Роль deutscher_assistant уже существует';
    END IF;
END
$$;

-- 2️⃣ Права на текущую базу
GRANT ALL PRIVILEGES ON DATABASE current_database() TO deutscher_assistant;

-- 3️⃣ Создание таблицы
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(100),
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    count BIGINT NOT NULL DEFAULT 0
);

-- 4️⃣ Права на таблицу
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO deutscher_assistant;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO deutscher_assistant;
