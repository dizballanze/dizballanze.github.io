Title: Node.JS - введение
Date: 2010-12-22 11:33
Author: Admin
Category: Node.js
Tags: java script, node.js
Lang: ru

![image][]

Сегодня я хочу рассмотреть библиотеку для асинхронного программирования
server-side приложений на Java Script - Node.JS.

Работает библиотека на Java Script движке V8 от самого гугла и
предоставляет базовые возможности для создания масштабируемых сетевых
приложений. Изначально Node заточен под высокие нагрузки, так что если
вы разрабатываете очередной facebook, то задумайтесь об использовании
server-side JS в своем приложении. Основная фишка библиотеки в работе с
HTTP протоколом, т.е. для нас web-разработчиков, то что доктор прописал.

Установка
---------

Я рассмотрю процесс установки в ОС Linux (Debian 5.0). Сначала скачиваем
архив с исходниками [здесь][]. Т.к. всё необходимое для работы
библиотеки включено в дистрибутив, то установка очень простая и знакома
всем линуксоидам, которые когда-либо собирали что-нибудь из исходников.
Итак, распаковываем архив, затем переходим в директорию с исходниками и
выполняем:

	:::bash
	./configure#make#make install

После этого можно проверить корректность установки, для этого
выполните:`make test`

Hello world
-----------

Теперь напишем простой пример web-сервера, который отвечает "Hello
World" на каждый запрос:

	:::javascript
	var http = require('http'); //Подключаем модуль http
	http.createServer(function (req, res) { //Создаем сервер и устанавливаем обработчик на подключение
	  res.writeHead(200, {'Content-Type': 'text/plain'}); //Устанавливаем заголовок
	  res.end('Hello World\n'); // Вывод сообщения и завершение вывода
	}).listen(8124, "127.0.0.1"); // Заставляем сервер "слушать" 127.0.0.1:8124
	console.log('Server running at http://127.0.0.1:8124/'); //Выводим сообщение в консоль

Для запуска нашего сервера выполняем:
	
	:::bash
	node example.jsServer running at http://127.0.0.1:8124/

Что-бы проверить, что всё работает открываем в браузере
http://127.0.0.1:8124 и получаем "Hello World" в ответ.

Таким способом мы получаем работающий web-сервер в несколько строк кода.
В скором времени будут ещё топики на тему Node.JS, в которых мы
подробнее рассмотрим процесс написания server-side JS приложений.

Ссылки
------

[nodejs.org][] - оф.сайт. Документация, новости проекта, примеры
приложений.

[nodejs.ru][] - русскоязычный блог о Node.js

  [image]: /media/2010/12/media_httpnodeblogfil_occie.png.scaled500.png
    "nodejs"
  [здесь]: http://nodejs.org/#download
  [nodejs.org]: http://nodejs.org/
  [nodejs.ru]: http://nodejs.ru
