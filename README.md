# Airline Service

REST API и веб-страница для авиакомпании на Flask и PostgreSQL.

## Обзор

Проект включает:
- Flask-приложение с SQLAlchemy
- PostgreSQL для хранения данных
- веб-страницу для ручной проверки API
- аутентификацию по телефону и паролю
- безопасное хранение паролей в виде хэшей
- Docker для локального запуска
- CI/CD-ориентированную структуру под TeamCity
- unit/интеграционные тесты на pytest

Основные маршруты:
- `GET /` — HTML-страница сервиса
- `GET /api/flights` — список рейсов
- `GET /api/miles?phone=<phone>&password=<password>` — мили пассажира (с аутентификацией)

---

## Структура проекта

### Корень проекта

- `README.md` — документация.
- `Dockerfile` — образ приложения на базе `python:3.9-slim`.
- `docker-compose.yml` — запуск `web` + `db` локально.
- `docker-compose.teamcity.yml` — TeamCity server + agent.
- `Dockerfile.teamcity-agent` — кастомный TeamCity agent с Python-инструментами.
- `entrypoint.sh` — запуск ожидания БД и Flask.
- `wait_for_db.py` — ожидание доступности PostgreSQL.
- `requirements.txt` — runtime-зависимости.
- `requirements-dev.txt` — dev-зависимости (pytest, flake8, bandit).
- `.flake8` — конфиг линтера.
- `commands` — примеры curl-запросов.

### Папка `app/`

- `app/__init__.py` — создание app, инициализация БД, seed-данные, миграция legacy-схемы паролей, роут `/`.
- `app/config.py` — конфигурация SQLAlchemy.
- `app/models.py` — модели `Flight` и `Passenger`.
- `app/routes.py` — API-роуты `/api/flights` и `/api/miles`.
- `app/templates/index.html` — UI для проверки функционала из браузера.

### Папка `tests/`

- `tests/test_app.py` — 20 автотестов (API, аутентификация, модели, ошибки, интеграция, HTML-страница).

### Папка `build/`

- `build/install` — установка зависимостей.
- `build/lint` — запуск flake8.
- `build/sast` — запуск bandit.
- `build/test` — запуск pytest.
- `build/push` — push Docker-образа.
- `build/deploy` — deploy-скрипт.

---

## Как работает приложение

### Инициализация

В `create_app()`:
- создаются таблицы,
- выполняется попытка расширить колонку пароля до `VARCHAR(255)` для старых БД,
- добавляются стартовые рейсы и пассажиры,
- пароли seed-пользователей сохраняются в хэшированном виде,
- legacy plaintext-пароли автоматически мигрируются в хэш при старте,
- регистрируются API-маршруты и корневой маршрут `/`.

### Модели

`Flight`:
- `id`
- `flight_number` (unique)
- `departure_airport`
- `arrival_airport`
- `departure_time`
- `duration`

`Passenger`:
- `id`
- `phone` (unique)
- `password` (хэш)
- `miles`

### Аутентификация

Эндпойнт `/api/miles`:
- принимает `phone` и `password`,
- ищет пассажира по телефону,
- проверяет пароль через `check_password_hash`,
- при ошибке возвращает `401`.

---

## Веб-страница

После запуска откройте:

- `http://localhost:5001/`

На странице доступны:
- загрузка списка рейсов,
- ввод телефона и пароля,
- получение миль,
- отображение ошибок (`Missing credentials`, `Invalid credentials`).

---

## Docker-запуск

```bash
docker compose down
docker compose up --build
```

Проверка:

- UI: `http://localhost:5001/`
- API: `http://localhost:5001/api/flights`

---

## Переменные окружения

Главная переменная:

- `DATABASE_URL` (по умолчанию `postgresql://user:password@db:5432/carsharing`)

Дополнительно в `docker-compose.yml`:

- `DB_HOST=db`
- `DB_PORT=5432`
- `DATABASE=postgres`

---

## Тестирование и качество

### Установка

```bash
./build/install
```

### Тесты

```bash
./build/test
```

Локально:

```bash
python -m pytest tests/test_app.py -v
```

Сейчас в проекте **20 тестов**:
- API рейсов,
- API миль и ошибки авторизации,
- HTML-страница `/`,
- модели и ограничения уникальности,
- интеграционные сценарии.

### Линтинг

```bash
./build/lint
```

### SAST

```bash
./build/sast
```

---

## TeamCity / CI/CD

Конфигурация TeamCity хранится в:

- `docker-compose.teamcity.yml`
- `Dockerfile.teamcity-agent`

Типовой pipeline:

- install
- lint
- sast
- test
- build
- push
- deploy

---

## Примеры API-запросов

```bash
# Список рейсов
curl http://localhost:5001/api/flights

# Успешная авторизация и мили
curl "http://localhost:5001/api/miles?phone=%2B7957285726&password=aercd112"

# Ошибка: нет параметров
curl "http://localhost:5001/api/miles"

# Ошибка: неверный пароль
curl "http://localhost:5001/api/miles?phone=%2B7957285726&password=wrongpassword"
```

---

## Тестовые данные

### Рейсы

| Номер | Аэропорт вылета | Аэропорт прилета | Время вылета | Длительность |
|---|---|---|---|---|
| 1 | Анапа | Внуково | 10:00 | 4:55 |
| 2 | Шереметьево | Калининград | 11:20 | 2:55 |
| 3 | Пулково | Шереметьево | 09:05 | 1:05 |
| 4 | Саратов | Толмачево | 11:25 | 5:02 |

### Пассажиры

| ID | Телефон | Мили |
|---|---|---|
| 1 | +7957285726 | 123 |
| 2 | +7957385621 | 91 |
| 3 | +79175715718 | 192 |

Примечание: в БД хранятся **хэши** паролей, не plaintext.

---

## Быстрый старт

```bash
docker compose up --build
```

Затем откройте `http://localhost:5001/` и проверьте:
- загрузку рейсов,
- успешную/неуспешную аутентификацию,
- получение миль.
