# Wagon Monorepo

Монорепозиторий проекта Wagon: бэкенд (FastAPI), фронтенд (Vue 3) и адаптер ЭТРАН.

## Быстрый старт

### Требования

- Docker и Docker Compose v2+

### Запуск

```bash
git clone <repo-url> && cd <repo>
docker compose up --build
```

Docker Compose поднимет четыре сервиса в правильном порядке:

1. **db** — PostgreSQL 16 (порт 5432)
2. **migrate** — применяет миграции Alembic и завершается
3. **api** — FastAPI-бэкенд (порт 8000)
4. **web** — Vue 3 фронтенд через nginx (порт 80)

### Доступные адреса

| Сервис        | URL                          |
|---------------|------------------------------|
| Фронтенд     | http://localhost              |
| API           | http://localhost:8000         |
| API-документация (Swagger) | http://localhost:8000/docs |

### Переменные окружения

Основные переменные задаются в `docker-compose.yml`. Для production рекомендуется переопределять через `.env` или `docker compose` override:

| Переменная       | Описание                        | По умолчанию                  |
|------------------|---------------------------------|-------------------------------|
| `POSTGRES_USER`  | Пользователь БД                 | `wagon`                       |
| `POSTGRES_PASSWORD` | Пароль БД                    | `wagon`                       |
| `POSTGRES_DB`    | Имя базы данных                 | `wagon_service`               |
| `DATABASE_URL`   | Строка подключения к БД         | `postgresql+asyncpg://wagon:wagon@db:5432/wagon_service` |
| `JWT_SECRET`     | Секрет для подписи JWT-токенов  | `change-me-in-production`     |

### Остановка

```bash
docker compose down
```

Для полного удаления данных (включая БД):

```bash
docker compose down -v
```
