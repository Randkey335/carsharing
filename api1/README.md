# Рекомендательные списки кафедр — REST API

REST API для управления рекомендательными списками учебных групп университета. Заведующий кафедрой может посмотреть, какие группы его кафедры включены в рекомендательный список на текущий семестр, и узнать их статус участия.

## Стек технологий

- **Python 3.11** + **Flask** — веб-фреймворк
- **PostgreSQL 15** — база данных
- **SQLAlchemy** — ORM
- **Gunicorn** — WSGI-сервер
- **Docker Compose** — оркестрация контейнеров
- **pytest** — тестирование

## Структура проекта

```
├── app/
│   ├── __init__.py      # Фабрика приложения (create_app)
│   ├── config.py        # Конфигурация (DATABASE_URL и т.д.)
│   ├── models.py        # Модели: Department, Manager, Group, RecommendationPeriod, RecommendationList
│   └── routes.py        # API-маршруты
├── tests/
│   ├── conftest.py      # Фикстуры pytest (SQLite in-memory для тестов)
│   ├── test_models.py   # Тесты моделей
│   └── test_routes.py   # Тесты API-маршрутов
├── docker-compose.yml   # Docker Compose: сервисы db и api
├── Dockerfile           # Образ Python-приложения
├── init.sql             # SQL-скрипт инициализации БД с тестовыми данными
├── requirements.txt     # Python-зависимости
└── commands.txt         # Шпаргалка с командами
```

## Модели базы данных

| Модель                  | Таблица                 | Описание                                                      |
|-------------------------|-------------------------|---------------------------------------------------------------|
| **Department**          | `departments`           | Кафедра (название, код)                                       |
| **Manager**             | `managers`              | Руководитель кафедры (ФИО, роль, привязка к кафедре)          |
| **Group**               | `groups`                | Учебная группа (название, курс, количество студентов, кафедра) |
| **RecommendationPeriod**| `recommendation_periods`| Период (семестр) с датами и флагом активности                  |
| **RecommendationList**  | `recommendation_lists`  | Запись рекомендательного списка (группа + период + статус)     |

### Статусы участия (`participation_status`)

| Значение      | Отображение             |
|---------------|-------------------------|
| `pending`     | Ожидает подтверждения   |
| `confirmed`   | Подтверждено            |
| `rejected`    | Отклонено               |
| `in_progress` | В процессе              |

## Запуск

### Требования

- Docker и Docker Compose

### Команды

```bash
# Запуск приложения (API + PostgreSQL) в фоне
docker compose up -d

# Остановка
docker compose down

# Пересборка после изменений в коде
docker compose up --build -d

# Запуск тестов в Docker
docker compose run --rm --no-deps api python -m pytest tests/ -v
```

После запуска:
- **API** доступно на `http://localhost:5002`
- **PostgreSQL** доступен на `localhost:5433` (пользователь: `admin`, пароль: `secret123`, БД: `university_db`)

## API-эндпоинты

### `GET /api/health`

Проверка работоспособности сервера.

```bash
curl http://localhost:5002/api/health
```

Ответ:
```json
{
  "status": "healthy",
  "message": "API работает"
}
```

---

### `GET /api/departments`

Список всех кафедр.

```bash
curl http://localhost:5002/api/departments
```

Ответ:
```json
{
  "success": true,
  "data": [
    {"id": 1, "name": "Кафедра информационных технологий", "code": "IT"},
    {"id": 2, "name": "Кафедра прикладной математики", "code": "PM"},
    {"id": 3, "name": "Кафедра программной инженерии", "code": "SE"}
  ]
}
```

---

### `GET /api/periods`

Список всех периодов (семестров), от новых к старым.

```bash
curl http://localhost:5002/api/periods
```

Ответ:
```json
{
  "success": true,
  "data": [
    {"id": 3, "name": "Осенний семестр 2026", "start_date": "2026-09-01", "end_date": "2026-12-31", "is_active": false},
    {"id": 2, "name": "Весенний семестр 2026", "start_date": "2026-02-01", "end_date": "2026-06-30", "is_active": true},
    {"id": 1, "name": "Осенний семестр 2025", "start_date": "2025-09-01", "end_date": "2025-12-31", "is_active": false}
  ]
}
```

---

### `GET /api/periods/current`

Текущий активный период (сегодняшняя дата попадает в диапазон дат и `is_active = true`).

```bash
curl http://localhost:5002/api/periods/current
```

Ответ `200`:
```json
{
  "success": true,
  "data": {"id": 2, "name": "Весенний семестр 2026", "start_date": "2026-02-01", "end_date": "2026-06-30", "is_active": true}
}
```

Ответ `404` (если активного периода нет):
```json
{
  "success": false,
  "error": "Активный период не найден"
}
```

---

### `GET /api/manager/<username>/groups`

**Основной эндпоинт.** По имени пользователя руководителя возвращает группы его кафедры из рекомендательного списка на текущий период.

```bash
curl http://localhost:5002/api/manager/ivanov/groups
curl http://localhost:5002/api/manager/sidorova/groups
```

Ответ `200`:
```json
{
  "success": true,
  "data": {
    "manager": {
      "id": 1,
      "username": "ivanov",
      "full_name": "Иванов Иван Иванович",
      "role": "Заведующий кафедрой"
    },
    "department": {
      "id": 1,
      "name": "Кафедра информационных технологий",
      "code": "IT"
    },
    "period": {
      "id": 2,
      "name": "Весенний семестр 2026",
      "start_date": "2026-02-01",
      "end_date": "2026-06-30",
      "is_active": true
    },
    "groups": [
      {
        "group_id": 1,
        "group_name": "ИВТ-21",
        "course": 4,
        "students_count": 25,
        "participation_status": "confirmed",
        "status_display": "Подтверждено",
        "recommendation_id": 1,
        "notes": "Группа подтвердила участие",
        "created_at": "2026-03-23T...",
        "updated_at": "2026-03-23T..."
      }
    ],
    "statistics": {
      "total": 6,
      "confirmed": 2,
      "pending": 2,
      "rejected": 1,
      "in_progress": 1
    }
  }
}
```

Ошибка `404` — руководитель не найден:
```json
{"success": false, "error": "Руководитель не найден", "error_code": "MANAGER_NOT_FOUND"}
```

Ошибка `404` — нет активного периода:
```json
{"success": false, "error": "Активный период рекомендаций не найден", "error_code": "NO_ACTIVE_PERIOD"}
```

## Тестирование

Тесты используют SQLite in-memory (не требуют PostgreSQL). 28 тестов покрывают все модели и маршруты.

```bash
docker compose run --rm --no-deps api python -m pytest tests/ -v
```

## Тестовые данные

При первом запуске в БД загружаются данные из `init.sql`:

- **3 кафедры:** IT, PM, SE
- **4 руководителя:** ivanov, petrov (кафедра IT), sidorova (PM), kozlov (SE)
- **3 периода:** осень 2025 (неактивен), весна 2026 (активен), осень 2026 (неактивен)
- **13 групп:** 6 на IT, 3 на PM, 4 на SE
- **13 записей** рекомендательного списка на весенний семестр 2026
