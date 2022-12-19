# Сервисы Admin Panel + ETL

Панель администратора для онлайн-кинотеатра.
## В проект входит
- GUI для работы с хранилищем
- Перенос данных из SQLite в Postgres
- API, позволяющий получить информацию об фильмах.
- Перенос данных из Postgres в ElasticSearch. 
- Инфраструктура для полнотекстового поиска

## Технологии
- [Python](https://www.python.org/) - is an interpreted high-level general-purpose programming language.
- [Django Framework](https://www.djangoproject.com/) - is a high-level Python Web framework that encourages rapid development and clean, pragmatic design.
- [PostgeSQL](https://www.postgresql.org/) - is an open source object-relational database system that uses and extends the SQL language combined with many features.
- [Docker](https://www.docker.com/) - is a set of platform as a service (PaaS) products that use OS-level virtualization to deliver software in packages (containers).
- [Gunicorn](https://gunicorn.org/) - is a Python WSGI HTTP Server for UNIX.
- [Nginx](https://nginx.org/) - is a web server that can also be used as a reverse proxy, load balancer, mail proxy and HTTP cache.

## Как развернуть проект
- скачать репозиторий, перейти в директорию с ```docker-compose.yml```

```git clone git@github.com:ваш-логин/new_admin_panel_sprint_3.git```

```cd etl```

- заполнить переменные среды в ```.env```
````
"""Postgresql"""
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT

"""Django"""
SECRET_KEY
DEBUG
DJANGO_SUPERUSER_USERNAME
DJANGO_SUPERUSER_PASSWORD
DJANGO_SUPERUSER_EMAIL

"""ElasticSearch"""
EL_HOST
El_PORT
EL_STORAGE
INDEX_NAME
CREATE_INDEX
INDEX_SETTINGS
````
В ```INDEX_SETTINGS``` устанавливаем схему. 
Используйте предложенную [cхему индекса](https://code.s3.yandex.net/middle-python/learning-materials/es_schema.txt)💾  `movies`, в которую должна производиться загрузка фильмов.
- Собрать и запустить докер-сборку

```docker-compose up -d --build```

```docker-compose up```

