Title: Настраиваем dev-сервер для удобной разработки на django
Date: 2012-12-22 22:55
Author: Admin
Category: Python
Tags: bitbucket, django, git, github, nginx, nodejs, pip, python, south
Lang: ru

При разработке не хочется тратить время, которого и так не хватает, на
рутинные действия. После каждой отправки изменений в репозиторий,
необходимо выполнить обновление кода на dev-сервере, применить миграции
и тд. Сегодня мы рассмотрим, как быстро настроить автоматический deploy
django-приложения на dev-сервер. Я рассмотрю максимально простое
решение, которое подойдет для небольших проектов.

![image][]

Требования к процессу
---------------------

Итак, давайте определимся какие именно действия необходимо
автоматизировать:

-   подгрузка изменений из репозитория
-   Установка зависимостей
-   Применение миграций
-   Перезагрузка web-сервера

Post-Receive Hooks
------------------

Необходимо каким-то образом отлавливать событие, когда пользователь
выполняет git push и запускать git pull на dev-сервере. Чаще всего я
использую github в качестве хостинга для git-репозиториев. Github
предоставляет возможность отправки POST-запроса на удаленный сервер,
после того как был получен push-запрос. Для этого необходимо прописать
url в настройках репозитория:

-   [GitHub][]
-   [Bitbucket][]

### Обработчик запросов

Как настроить отправку запросов мы узнали, теперь необходимо реализовать
обработчик запросов. Можно обрабатывать запросы в самом приложении или
отдельно, вот небольшой пример на node.js:

	:::javascript
	http = require('http')
	var exec = require('child_process').exec
	  , child;
	server = http.createServer(function(req, res) {
		res.writeHead(200, {'Content-Type': 'text/plain'});
		res.end();
		child = exec('/path/to/project/deploy.sh', function(error, out, err){
			if (error) console.error(error);
		});
	}).listen(8000, '0.0.0.0');
	console.log('Git monitor server is running at 0.0.0.0:8000');

Здесь, при поступлении любого запроса, просто выполняется bash скрипт.
При желании можно добавить дополнительные действия, например логировать
запросы или добавить валидацию, чтобы запрос мог поступать только с
определенных серверов.

Далее просто нужно добавить адрес, на котором весит наш демон, в
настройках github/bitbucket.

Применяем изменения
-------------------

В обработчике запросов мы выполняем bash скрипт. Рассмотрим пример того,
что может содержать такой скрипт:

	:::bash
	#!/bin/bash
	cd /path/to/project/dir
	# update code
	git pull
	# activate virtualenv
	source ../bin/activate
	# install new packages with pip
	pip install -r ./requirements.txt
	# Sync db changes
	app/manage.py syncdb
	app/manage.py migrate --all --merge
	# kill runserver
	killall python
	nohup app/manage.py 
	runserver 0.0.0.0:9000 &

Итак, что здесь происходит:

-   Переходим в директорию проекта
-   Выполняем загрузку изменений с репозитория
-   Активируем virtualenv (я надеюсь вы его используете :))
-   Устанавливаем новые пакеты
-   Применяем миграции south
-   Перезапускаем web-сервер

Здесь все достаточно просто, рассмотрим только как осуществляется
управление пакетами. При установке нового пакета необходимо добавить его
в текстовый файл. Создать такой файл можно автоматически при помощи
следующей команды:

	:::text
	pip freeze > requirements.txt

Данная команда сформирует список всех установленных пакетов и также
укажет их версии. Вот пример сгенерированного файла:

	:::text
	Django==1.4.2
	PIL==1.1.7
	South==0.7.6
	argparse==1.2.1
	lxml==3.0.1
	....
	mongoengine==0.7.5
	psycopg2==2.4.5
	pymongo==2.3
	python-dateutil==2.1

При выполнении нашего bash-скрипта будет вызвана команда:

	:::text
	pip install -r ./requirements.txt

Это приведет к установке всех пакетов, из списка в файле, которые ещё
небыли установлены.

Конечно, в зависимости от ваших потребностей, могут понадобится
дополнительные действия, например трансляция CoffeeScript, Compass или
выполнение тестов. Добавить новые команды в скрипт, я думаю, не составит
трудностей :)

Настройка Nginx
---------------

Для того, чтобы перенаправлять запросы с 80 порта на runserver я
использую nginx (ну не запускать же runserver от root'а :)). Пример
конфигурации nginx:

	:::nginx
	user www-data;
	worker_processes 4;
	pid /var/run/nginx.pid;

	events {
		worker_connections 768;
	}

	http {

		##
		# Basic Settings
		##

		sendfile on;
		tcp_nopush on;
		tcp_nodelay on;
		keepalive_timeout 65;
		types_hash_max_size 2048;

		include /etc/nginx/mime.types;
		default_type application/octet-stream;

		##
		# Logging Settings
		##

		access_log /var/log/nginx/access.log;
		error_log /var/log/nginx/error.log;

		##
		# Proxy Settings
		##
		server {
			listen *:80;

			location / {
				proxy_pass	http://localhost:9000;
				proxy_set_header	Host $host;
				proxy_set_header X-Real-IP $remote_addr;
			}
		}
	}

На этом все, пишите в комментариях, если я что-то упустил.

  [image]: /media/2012/12/FotoFlexer_Photo.jpg
  [GitHub]: https://help.github.com/articles/post-receive-hooks
  [Bitbucket]: https://confluence.atlassian.com/display/BITBUCKET/POST+Service+Management
