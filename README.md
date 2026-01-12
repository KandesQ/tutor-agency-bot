# В рамках проекта реализовано

- ### Оплата занятий через платежную систему ЮKassa
- ### Регистрация с использованием одноразового кода
- ### Отчет по оплатам занятий учениками в виде excel-файла
- ### Соглашение на обработку ПДн
- ### Отчет о месячном доходе

<hr>

## Развертка

В корне проекта создайте **.env** файл:
```.dotenv
# postgres
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=...
DB_NAME=tutor_agency_bot

# telegram
HEAD_MANAGER_ID=...
BOT_TOKEN=...

JWT_SECRET=...

# Redis
REDIS_PASSWORD=...
REDIS_HOST=...
REDIS_PORT=...

# app
# Версия пользовательского соглашения
CONSENT_VERSION=...
```

Установите зависимости:
```bash
pip install -r requirements.txt
```

Запустите контейнеры в [Docker](https://www.docker.com/get-started/):
```bash
docker compose up -d
```

Запустите миграции:
```bash
alembic upgrade head
```

Если получаете ошибку вида:
```bash
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server at "localhost" (::1), port 5432 failed: server closed the connection unexpectedly
        This probably means the server terminated abnormally                                                                                                                                                                                                                                                        
        before or while processing the request.  
```
Подождите пока контейнеры запустятся (5-10 секунд)

Запустите бота:
```bash
    python ./bot/main.py
```

\-