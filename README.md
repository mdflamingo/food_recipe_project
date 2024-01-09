## Фудграм
Это полностью рабочий проект, который состоит из бэкенд-приложения на Django и фронтенд-приложения на React. Сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Проект состоит из следующих страниц: 
- главная,
- страница рецепта,
- страница пользователя,
- страница подписок,
- избранное,
- список покупок,
- создание и редактирование рецепта.

## Установка
1. Клонируйте репозиторий на свой компьютер:

```
  git clone git@github.com:mdflamingo/foodgram-project-react
```
2. Создайте файл .env и заполните его своими данными. Перечень данных указан в корневой директории проекта в файле .env.

## Создание Docker-образов
1. Замените username на ваш логин на Dockerhub:
```
  cd frontend
  docker build -t username/foodgram_frontend .
  cd ../foodgram_project
  docker build -t username/foodgram_backend .
```
2. Загрузите образы на DockerHub:
```
  docker push username/foodgram_frontend
  docker push username/foodgram_backend
```
## Деплой на сервере
1. Подключитесь к удаленному серверу
```
  ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера
```

3. Создайте на сервере директорию kittygram через терминал
```
  mkdir foodgram
```
3. Установка docker compose на сервер:
```
  sudo apt update
  sudo apt install curl
  curl -fSL https://get.docker.com -o get-docker.sh
  sudo sh ./get-docker.sh
  sudo apt-get install docker-compose-plugin
```
4. В директорию foodgram/ скопируйте файлы docker-compose.production.yml и .env, nginx.conf:
```
  scp -i path_to_SSH/SSH_name docker-compose.production.yml username@server_ip:/home/username/foodgram/docker-compose.production.yml
  * ath_to_SSH — путь к файлу с SSH-ключом;
  * SSH_name — имя файла с SSH-ключом (без расширения);
  * username — ваше имя пользователя на сервере;
  * server_ip — IP вашего сервера.
```
5. Запустите docker compose в режиме демона:
```
  sudo docker compose -f docker-compose.production.yml up -d
```
6. Выполните миграции, импортируйте ингредиенты из csv-файла, соберите статические файлы бэкенда и скопируйте их в /backend_static/static/,
создайте суперпользователя:
```
  sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
  sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
  sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
  sudo docker compose -f docker-compose.production.yml exec backend python manage.py runscript impoprt_csv
  sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser

```
7. На сервере в редакторе nano откройте конфиг Nginx:
```
  sudo nano /etc/nginx/sites-enabled/default
```
8. Измените настройки location в секции server:
```
  location / {
      proxy_set_header Host $http_host;
      proxy_pass http://127.0.0.1:8000;
  }
```
9. Проверьте работоспособность конфига Nginx:
```
  sudo nginx -t
```
Если ответ в терминале такой, значит, ошибок нет:
```
  nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
  nginx: configuration file /etc/nginx/nginx.conf test is successful
```
10. Перезапускаем Nginx
```
  sudo service nginx reload
```

## Автор
Анастасия Вольнова
