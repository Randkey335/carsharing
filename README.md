# Airline Service

REST API-сервис для авиакомпании на Flask и PostgreSQL.

## Обзор

Проект реализует:
- веб-сервис на Flask
- ORM через Flask-SQLAlchemy
- PostgreSQL как хранилище данных
- Docker-окружение для локального запуска
- CI/CD-ориентированные конфигурации для TeamCity
- unit-тесты с pytest (19 полностью автоматизированных тестов)
- вспомогательные скрипты для сборки, линтинга, тестирования и анализа безопасности

Сервис предоставляет два основных API-эндпойнта:
- `GET /api/flights` — список всех рейсов с информацией о времени, аэропортах и длительности
- `GET /api/miles?phone=<phone>&password=<password>` — информация о накопленных милях пассажира (требует аутентификацию)

---

## Структура проекта

### Корневые файлы

- `README.md` — этот файл.
- `Dockerfile` — образ для приложения, на основе `python:3.9-slim`.
- `docker-compose.yml` — конфигурация для локального запуска приложения и PostgreSQL.
- `docker-compose.teamcity.yml` — конфигурация для запуска TeamCity server + agent.
- `Dockerfile.teamcity-agent` — кастомный образ TeamCity agent, в котором установлены Python и dev-зависимости.
- `entrypoint.sh` — стартовый скрипт контейнера `web`.
- `wait_for_db.py` — скрипт ожидания доступности PostgreSQL.
- `requirements.txt` — runtime-зависимости приложения.
- `requirements-dev.txt` — dev-зависимости для тестов, линтинга и анализа безопасности.
- `.flake8` — правила проверки кода.
- `commands` — примеры HTTP-запросов к API.

### Каталог `app/`

- `app/__init__.py` — создание Flask-приложения, инициализация БД, создание таблиц и импорт маршрутов.
- `app/config.py` — конфигурация SQLAlchemy.
- `app/models.py` — модели данных `Flight` и `Passenger`.
- `app/routes.py` — API-маршруты.

### Каталог `tests/`

- `tests/__init__.py` — инициализация тестовой папки.
- `tests/test_app.py` — 19 unit-тестов для моделей, маршрутов, аутентификации и обработчиков ошибок.

### Каталог `build/`

В каталоге `build/` находятся скрипты для автоматизации сборки и проверки:
- `build/install` — установка пакетов Python.
- `build/lint` — запуск `flake8` для проверки стиля.
- `build/sast` — запуск `bandit` для анализа безопасности.
- `build/test` — запуск `pytest` для unit-тестов.
- `build/push` — пуш Docker-образа в реестр.
- `build/deploy` — деплой на сервер.

---

## Как это работает

### Приложение и инициализация

`app/__init__.py` создаёт Flask-приложение через `create_app()`:
- загружает настройки из `app.config.Config`
- инициализирует SQLAlchemy
- создаёт таблицы при старте через `db.create_all()`
- заполняет БД начальными данными, если таблицы пусты:
  - 4 рейса (`Flight`)
  - 3 пассажира (`Passenger`)
- регистрирует blueprint из `app.routes`
- добавляет обработчики ошибок 401 и 404

### Конфигурация БД

`app/config.py` использует переменную окружения `DATABASE_URL`.
Если она не задана, по умолчанию берётся строка:

```python
postgresql://user:password@db:5432/carsharing
```

### Модели

`app/models.py` содержит две таблицы:

- `Flight`
  - `id` — primary key
  - `flight_number` — номер рейса, уникальное поле
  - `departure_airport` — аэропорт вылета
  - `arrival_airport` — аэропорт прилета
  - `departure_time` — время вылета (формат HH:MM)
  - `duration` — длительность полёта (формат HH:MM)

- `Passenger`
  - `id` — primary key
  - `phone` — номер телефона пассажира, уникальное поле
  - `password` — пароль для аутентификации
  - `miles` — количество накопленных миль

### Маршруты API

`app/routes.py` содержит URL-эндпойнты:

- `GET /api/flights`
  - возвращает список всех рейсов
  - ответ JSON-массив с полями:
    - `flight_number` — номер рейса
    - `departure_airport` — аэропорт вылета
    - `arrival_airport` — аэропорт прилета
    - `departure_time` — время вылета
    - `duration` — длительность полёта

- `GET /api/miles`
  - принимает query-параметры `phone` и `password`
  - проверяет пару телефон-пароль в БД
  - если нет — возвращает 401
  - возвращает JSON с полями:
    - `miles` — количество миль пассажира
    - `phone` — номер телефона пассажира

---

## Docker-сборка и запуск

### Локальный запуск

1. Убедитесь, что установлен Docker.
2. Выполните:

```bash
docker compose up --build
```

3. В браузере или curl используйте `http://localhost:5001/api/flights`.

### Что делает контейнер `web`

`Dockerfile` строит образ на Python 3.9, устанавливает зависимости и копирует код.

`entrypoint.sh` выполняет:

```sh
python wait_for_db.py
python -m flask run --host=0.0.0.0
```

Это гарантирует, что веб-приложение стартует только после готовности PostgreSQL.

### Ожидание БД

`wait_for_db.py` выполняет бесконечный цикл, пока PostgreSQL не станет доступным по `DATABASE_URL`.

---

## Переменные окружения

Основная переменная:

- `DATABASE_URL` — строка подключения к PostgreSQL.

Примеры из `docker-compose.yml`:

- `postgresql://user:password@db:5432/carsharing`
- `DB_HOST=db`
- `DB_PORT=5432`
- `DATABASE=postgres`

Для локального запуска можно установить переменную явно:

```bash
set DATABASE_URL=postgresql://user:password@localhost:5432/carsharing
```

---

## Тестирование и линтинг

### Установка зависимостей

```bash
./build/install
```

### Unit-тесты

```bash
./build/test
```

Проект содержит 19 полностью автоматизированных unit-тестов:
- 3 теста для API рейсов
- 8 тестов для аутентификации и получения миль
- 4 теста для моделей БД (создание, уникальность)
- 2 теста для обработчиков ошибок
- 2 интеграционных теста

Для локального запуска:
```bash
python -m pytest tests/test_app.py -v
```

### Проверка стиля

```bash
./build/lint
```

### Анализ безопасности

```bash
./build/sast
```

> В `requirements-dev.txt` находятся инструменты `pytest`, `flake8`, `bandit`.

---

## TeamCity / CI

В репозитории есть конфигурация для TeamCity:

- `docker-compose.teamcity.yml` — поднимает `teamcity-server` и `teamcity-agent` в Docker.
- `Dockerfile.teamcity-agent` — устанавливает Python и пакеты из `requirements-dev.txt`.

`Dockerfile.teamcity-agent` также устанавливает специальный `ENTRYPOINT`, который даёт агенту доступ к Docker-сокету.

---

## Примеры запросов

Файл `commands` содержит curl-примеры:

```bash
# Получить список всех рейсов
curl http://localhost:5001/api/flights

# Получить накопленные мили со льготой (успешные учетные данные)
curl "http://localhost:5001/api/miles?phone=%2B7957285726&password=aercd112"

# Получить накопленные мили второго пассажира
curl "http://localhost:5001/api/miles?phone=%2B7957385621&password=okliuj91"

# Получить накопленные мили третьего пассажира
curl "http://localhost:5001/api/miles?phone=%2B79175715718&password=09ikjhbn12"

# Нет параметров - 401
curl "http://localhost:5001/api/miles"

# Неверный пароль - 401
curl "http://localhost:5001/api/miles?phone=%2B7957285726&password=wrongpassword"

# Несуществующий телефон - 401
curl "http://localhost:5001/api/miles?phone=%2B79999999999&password=password"
```

## Примеры данных

### Рейсы (Flights)

| Номер | Аэропорт вылета | Аэропорт прилета | Время вылета | Длительность |
|-------|-----------------|------------------|-------------|-------------|
| 1     | Анапа           | Внуково          | 10:00       | 4:55        |
| 2     | Шереметьево     | Калининград      | 11:20       | 2:55        |
| 3     | Пулково         | Шереметьево      | 09:05       | 1:05        |
| 4     | Саратов         | Толмачево        | 11:25       | 5:02        |

### Пассажиры (Passengers)

| ID | Номер телефона  | Пароль     | Мили |
|----|-----------------|-----------|------|
| 1  | +7957285726     | aercd112  | 123  |
| 2  | +7957385621     | okliuj91  | 91   |
| 3  | +79175715718    | 09ikjhbn12| 192  |

---

## Замечания

- В `docker-compose.yml` сервис `web` зависит от `db`, но `depends_on` не гарантирует, что PostgreSQL уже готов к соединениям. Для этого используется `wait_for_db.py`.
- Стартовая инициализация данных выполняется автоматически при первом запуске.
- Unit-тесты охватывают все основные компоненты системы: модели, маршруты, аутентификацию и обработку ошибок.
- Аутентификация происходит через сравнение телефона и пароля из query-параметров с данными в БД.
- Для реального продакшена стоит добавить миграции (`Flask-Migrate` или Alembic), отдельный prod-файл `docker-compose.prod.yml`, безопасное управление секретами и HTTPS.

---

## Быстрый старт

```bash
docker compose up --build
```

Откройте `http://localhost:5001/api/flights` для получения списка всех рейсов.

Затем запросите мили пассажира:
```bash
curl "http://localhost:5001/api/miles?phone=%2B7957285726&password=aercd112"
```

Для запуска unit-тестов локально:
```bash
python -m pytest tests/test_app.py -v
```
