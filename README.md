[![Main foodgram workflow](https://github.com/ViolettaValieva/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/ViolettaValieva/foodgram/actions/workflows/main.yml)

![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

## Описание проекта
Проект «Фудграм» — сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

**Посетить сайт**: https://foodgram-foryou.hopto.org/
## Стек

- Python 3.9
- Django 3.2.3
- Django REST framework 3.12.4
- JavaScript
- Nginx
- Docker compose

## Запуск проекта

Клонируйте репозиторий с проектом на свой компьютер.
В терминале из рабочей директории выполните команду:
```bash
git clone https://github.com/ViolettaValieva/foodgram.git
```
Создайте файл .env и заполните его своими данными по примеру.

    ```bash
    POSTGRES_DB=django
    POSTGRES_USER=django_user
    POSTGRES_PASSWORD=password
    DB_HOST=db
    DB_PORT=5432
    DEBUG=False
    SECRET_KEY=django_secret_key_example
    ```

Выполните команду:
```bash
cd ../infra
docker compose up
```  
Произойдет создание и включение контейнеров, создание томов и сети.
### Миграции, сбор статистики

После запуска нужно выполнить сбор статистики и миграции. Статистика фронтенда собирается во время запуска контейнера, после чего он останавливается.:
```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic
docker compose exec backend python manage.py cp -r /app/collected_static/. /static/static/
```

### Заполните базу тестовыми данными:
```bash
docker-compose exec backend python manage.py load_data 
```
Теперь проект доступен на: 
```
http://localhost:8000/
```
А спецификация API по адресу:
```
http://localhost:8000/api/docs/
```
## Остановка

В окне, где был запуск **Ctrl+С** или в другом окне:

```bash
sudo docker compose down
```

## Автор

[ViolettaValieva](https://github.com/ViolettaValieva)

