# Тестовое задание (Instagram Sync Service)

Сервис на базе **Django + DRF** для синхронизации контента из Instagram в локальную базу данных и управления комментариями.

## Архитектура проекта

1.  **Models**: `Post` и `Comment`. Хранят данные Instagram. Используется логика Upsert для обновления существующих записей.
2.  **Clients**: `InstagramClient`. Низкоуровневая обертка над Instagram Graph API. Обрабатывает HTTP-запросы, авторизацию и автоматическую пагинацию (обход всех страниц через `next`).
3.  **Services**: `SyncService`. Содержит высокоуровневую бизнес-логику синхронизации, связывая клиент API и модели данных.
4.  **Views & Serializers**:
    *   `SyncView`: Триггер синхронизации.
    *   `PostListView`: Список постов с пагинацией `CursorPagination`.
    *   `CommentCreateView`: Создание комментария. Включает двойную проверку (наличие поста в локальной БД и его валидность в Instagram API).

## Технологический стек

*   **Python 3.11+**
*   **Django & Django REST Framework**
*   **PostgreSQL**
*   **Docker & Docker Compose**
*   **Pytest**

## Быстрый старт

1.  **Клонируйте репозиторий.**
2.  **Настройте переменные окружения:**
    Создайте файл `.env` на основе `.env.example`.
    ```bash
    cp .env.example .env
    ```
    Обязательно укажите `INSTAGRAM_ACCESS_TOKEN`.

3.  **Запустите проект через Docker Compose:**
    ```bash
    docker-compose up --build
    ```

4.  **Примените миграции (если проект запущен):**
    ```bash
    docker-compose exec web python manage.py migrate
    ```

## Тестирование

Запуск всех тестов (интеграционные тесты с моками внешнего API):
```bash
docker-compose exec web pytest
```

## Документация API

После запуска проекта документация доступна по адресу:
*   **Swagger UI:** `http://localhost:8000/api/schema/swagger-ui/`

