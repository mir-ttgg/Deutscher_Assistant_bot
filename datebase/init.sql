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

-- 2️⃣ Права на базу
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO deutscher_assistant;

-- 3️⃣ Создание таблицы users
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(100),
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    count BIGINT NOT NULL DEFAULT 0,
    last_reset TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4️⃣ Создание таблицы queries (вопросы-ответы)
CREATE TABLE IF NOT EXISTS queries (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5️⃣ Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_queries_user_id ON queries(user_id);
CREATE INDEX IF NOT EXISTS idx_queries_created_at ON queries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_users_last_reset ON users(last_reset);

-- 6️⃣ Права на таблицы
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO deutscher_assistant;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO deutscher_assistant;

-- 7️⃣ Комментарии
COMMENT ON COLUMN users.count IS 'Количество запросов за текущую неделю';
COMMENT ON COLUMN users.last_reset IS 'Дата последнего сброса счетчика (понедельник 00:00 МСК)';
COMMENT ON TABLE queries IS 'История всех вопросов и ответов для отчетов';