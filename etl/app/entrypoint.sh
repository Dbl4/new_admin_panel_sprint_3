#!/bin/sh
if [ "$DATABASE" = "postgres" ]
then
    # если база еще не запущена
    echo "DB not yet run..."
    # Проверяем доступность хоста и порта
    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done
    echo "DB did run."
fi

# shellcheck disable=SC2164
cd /app

# Удаляем все старые данные
python manage.py flush --no-input
# Создаем миграции и выполняем миграции
python manage.py makemigrations
python manage.py migrate
# создаем суперпользователя
python manage.py createsuperuser --noinput
# Собираем файлы статики
python manage.py collectstatic --noinput
gunicorn --bind 0.0.0.0:8000 config.wsgi
exec "$@"