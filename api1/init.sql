-- Создание таблиц

-- Таблица кафедр
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL
);

-- Таблица руководителей
CREATE TABLE IF NOT EXISTS managers (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(100) NOT NULL,
    department_id INTEGER REFERENCES departments(id)
);

-- Таблица периодов рекомендаций
CREATE TABLE IF NOT EXISTS recommendation_periods (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Таблица групп
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    course INTEGER NOT NULL,
    students_count INTEGER DEFAULT 0
);

-- Таблица рекомендательных списков
CREATE TABLE IF NOT EXISTS recommendation_lists (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups(id),
    period_id INTEGER REFERENCES recommendation_periods(id),
    participation_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_groups_department ON groups(department_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_lists_period ON recommendation_lists(period_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_lists_group ON recommendation_lists(group_id);
CREATE INDEX IF NOT EXISTS idx_managers_department ON managers(department_id);

-- =====================================================
-- ТЕСТОВЫЕ ДАННЫЕ
-- =====================================================

-- Кафедры
INSERT INTO departments (name, code) VALUES 
    ('Кафедра информационных технологий', 'IT'),
    ('Кафедра прикладной математики', 'PM'),
    ('Кафедра программной инженерии', 'SE')
ON CONFLICT (code) DO NOTHING;

-- Руководители
INSERT INTO managers (username, full_name, role, department_id) VALUES 
    ('ivanov', 'Иванов Иван Иванович', 'Заведующий кафедрой', 1),
    ('petrov', 'Петров Петр Петрович', 'Заместитель заведующего', 1),
    ('sidorova', 'Сидорова Анна Михайловна', 'Заведующий кафедрой', 2),
    ('kozlov', 'Козлов Дмитрий Сергеевич', 'Заведующий кафедрой', 3)
ON CONFLICT (username) DO NOTHING;

-- Периоды рекомендаций (текущий период: весенний семестр 2026)
INSERT INTO recommendation_periods (name, start_date, end_date, is_active) VALUES 
    ('Осенний семестр 2025', '2025-09-01', '2025-12-31', FALSE),
    ('Весенний семестр 2026', '2026-02-01', '2026-06-30', TRUE),
    ('Осенний семестр 2026', '2026-09-01', '2026-12-31', FALSE);

-- Группы кафедры IT
INSERT INTO groups (name, department_id, course, students_count) VALUES 
    ('ИВТ-21', 1, 4, 25),
    ('ИВТ-22', 1, 3, 28),
    ('ИВТ-23', 1, 2, 30),
    ('ИВТ-24', 1, 1, 32),
    ('КБ-22', 1, 3, 22),
    ('КБ-23', 1, 2, 24);

-- Группы кафедры PM
INSERT INTO groups (name, department_id, course, students_count) VALUES 
    ('ПМ-21', 2, 4, 20),
    ('ПМ-22', 2, 3, 22),
    ('ПМ-23', 2, 2, 25);

-- Группы кафедры SE
INSERT INTO groups (name, department_id, course, students_count) VALUES 
    ('ПИ-21', 3, 4, 26),
    ('ПИ-22', 3, 3, 28),
    ('ПИ-23', 3, 2, 27),
    ('ПИ-24', 3, 1, 30);

-- Рекомендательные списки на текущий период (весенний семестр 2026)
-- Для кафедры IT (department_id = 1)
INSERT INTO recommendation_lists (group_id, period_id, participation_status, notes) VALUES 
    (1, 2, 'confirmed', 'Группа подтвердила участие'),
    (2, 2, 'in_progress', 'Ожидается подтверждение от куратора'),
    (3, 2, 'pending', NULL),
    (4, 2, 'pending', 'Первокурсники - требуется согласование'),
    (5, 2, 'confirmed', 'Участвует в полном составе'),
    (6, 2, 'rejected', 'Конфликт расписания');

-- Для кафедры PM (department_id = 2)
INSERT INTO recommendation_lists (group_id, period_id, participation_status, notes) VALUES 
    (7, 2, 'confirmed', NULL),
    (8, 2, 'pending', NULL),
    (9, 2, 'in_progress', 'Ждём ответа');

-- Для кафедры SE (department_id = 3)
INSERT INTO recommendation_lists (group_id, period_id, participation_status, notes) VALUES 
    (10, 2, 'confirmed', 'Полная готовность'),
    (11, 2, 'confirmed', NULL),
    (12, 2, 'pending', NULL),
    (13, 2, 'pending', 'Новая группа');
