### **foodgrammm.hopto.org**


### **Описание проекта:**

Проект «Продуктовый помощник» («Foodgram») — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.


### **Используемые технологии:**

Python 3, Django, Django Rest Framework, Djoser, React, PostgreSQL, Docker, Nginx, Gunicorn, Continuous Integration, Continuous Deployment.

Веб-сервер: Nginx (контейнер nginx)
Frontend: React (контейнер frontend)
Backend: Django (контейнер backend)
API: Django REST (контейнер backend)
База данных: PostgreSQL (контейнер db)


### **База данных и переменные окружения:**

Проект использует базу данных PostgreSQL.
Для подключения и выполненя запросов к базе данных необходимо создать файл ".env" в папке "./infra/".

Шаблон для заполнения файла ".env":

> DB_ENGINE=django.db.backends.postgresql
> DB_NAME=postgres
> POSTGRES_USER=postgres
> POSTGRES_PASSWORD=postgres
> DB_HOST=db
> DB_PORT=5432
> SECRET_KEY='Здесь указать секретный ключ'
> ALLOWED_HOSTS='Здесь указать имя или IP хоста' (для локального запуска - 127.0.0.1)
> DEBUG=False


### **Как запустить проект локально:**

Клонировать репозиторий и перейти в него в командной строке:

> git clone git@github.com:katekatekatem/foodgram-project-react.git
> 
> cd foodgram-project-react

Перейдите в папку infra и запустите оркестр контейнеров:

> cd infra
> 
> docker-compose up -d

После успешного запуска контейнеров выполните миграции:

> docker exec infra-backend-1 python manage.py migrate

Создать суперюзера:

> docker exec -it infra-backend-1 python manage.py createsuperuser

Заполнить данные из БД:

> docker exec infra-backend-1 python manage.py import_data


Запустится проект и будет доступен по адресу [localhost:7001](http://localhost:7001/).

После запуска проекта документация будет доступна по ссылке по ссылке - [localhost:7001/api/docs/](http://localhost:7001/api/docs/).


### **Автор проекта:**

Екатерина Мужжухина
Python Backend Developer
github: katekatekatem
e-mail: muzhzhukhina@mail.ru
