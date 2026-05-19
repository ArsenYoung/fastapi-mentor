# FastAPI Test

Простой FastAPI-проект с PostgreSQL в Docker и миграциями Alembic.

## Структура проекта

- `src/` — исходный код приложения
  - `src/application.py` — функция `get_app()` для создания FastAPI-приложения
  - `src/main.py` — запуск приложения через Uvicorn (factory)
  - `src/config.py` — конфигурация проекта
  - `src/db.py` — подключение к базе данных
  - `src/models/` — SQLAlchemy модели
- `alembic/` — файлы Alembic
- `alembic.ini` — конфигурация Alembic
- `docker-compose.yaml` — Docker Compose для PostgreSQL
- `pyproject.toml` — управление пакетами через Poetry

## Запуск сервиса

### Через Uvicorn

Запустить приложение из корня проекта:

```bash
cd /home/arsenii/Documents/Projects/Fastapi-test
source .venv/bin/activate
uvicorn src.application:get_app --reload --factory
```

Если хочется запускать через `src/main.py`:

```bash
python src/main.py
```

## Docker Compose

### Запуск базы данных

```bash
docker compose up -d
```

### Остановка базы данных

```bash
docker compose down
```

### Проверка контейнеров

```bash
docker ps
```

### Если порт 5432 уже занят

В проекте настроен PostgreSQL на хосте `5432`. Если на этой машине уже есть другой контейнер или служба на порту `5432`, остановите его или измените порт в `docker-compose.yaml` и в `alembic.ini`.

## Работа с Poetry

### Установка зависимостей

```bash
poetry install
```

### Добавление пакета

```bash
poetry add <package>
```

### Удаление пакета

```bash
poetry remove <package>
```

### Вход в виртуальное окружение

```bash
poetry shell
```

### Запуск команды внутри среды Poetry

```bash
poetry run <command>
```

## Alembic

### Проверка конфигурации

В `alembic.ini` используется строка подключения:

```ini
sqlalchemy.url = postgresql+asyncpg://postgres:123456@localhost:5432/postgres
```

Если Docker-сервис работает на другом порту, замените `5432` на нужный.

### Создание миграции

```bash
alembic revision --autogenerate -m "init"
```

### Применение миграций

```bash
alembic upgrade head
```

### Отмена миграций

```bash
alembic downgrade -1
```

## Полезные примечания

- Главный модуль приложения находится в `src/application.py`, поэтому при запуске `uvicorn` нужно указывать именно этот путь.
- Если `uvicorn main:app --reload` выдаёт ошибку `Could not import module "main"`, значит файл `main.py` отсутствует в корне проекта.
- Убедитесь, что пакет `asyncpg` установлен, если используется асинхронная строка подключения к PostgreSQL.
- Для работы Alembic необходимо, чтобы контейнер PostgreSQL был доступен и авторизация проходила с указанными логином/паролем.
