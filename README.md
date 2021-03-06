# Социальная сеть для публикации блогов.
# Описание
Пользователи могут создавать свои страницы, делать записи и прикреплять к ним изображения. Если зайти на страницу пользователя, то можно посмотреть все записи автора, подписаться на него, и оставлять комментарии. Есть возможность модерировать записи и блокировать пользователей, реализовано через админ-панель.

# Стек технологий

Python 3.8, Django 2.2.19, DjangoORM, SQLite

# Запуск проекта

Создание и активация виртуального окружения:
```
python3 -m venv venv
source venv/Scripts/activate
```
Установка зависимостей из файла requirements.txt:
```
pip install -r requirements.txt
```
Применить миграции:
```
python manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver
```
