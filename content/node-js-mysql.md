Title: Node.JS + MySQL
Date: 2011-03-28 18:47
Author: Admin
Category: Node.js
Tags: MySQL, node-mysql, node.js

![Mysql + Node.js][]

В последнем проекте появилась необходимость
организации работы Node.JS с MySQL. Для создания данного взаимодействия
существует несколько модулей, я решил использовать **node-mysql**, т.к.
он предоставляет все необходимые мне функции.

Установка node-mysql
--------------------

Для установки воспользуемся git:

	:::bash
	cd ~/.node_libraries
	git clone git://github.com/felixge/node-mysql.git mysql

После этого вы можете без проблем использовать данный модуль в вашей
работе.

Установка соединения
--------------------

Перед началом выполнения запросов к БД необходимо выполнить подключение
к серверу MySQL. Рассмотрим как сделать это при помощи модуля node-mysql
в node.js:

	:::javascript
	var Client = require('mysql').Client,
    client = new Client();
	client.user = 'root';
	client.password = 'password';
	client.connect();
	client.end();

Первые две строки отвечают за подключение модуля и создания
объекта-клиента. Далее задаются параметры аутентификации и вызывается
метод connect. После этого если вы корректно указали пару логин-пароль,
то будет установлено соединение. Последняя строка соответственно
завершает соединение с сервером.

### Отступление

Для того что-бы наш MySQL клиент мог передать данные аутентификации
необходимо чтобы node.js был скомпилирован с поддержкой ssl, иначе при
попытке установления соединения он будет жутко ругатся из-за то что не
сможет зашифровать пароль. Для корректной компиляции node.js с
поддержкой ssl в Debian вам потребуется пакет libssl-dev

Выполнение запросов
-------------------

Сначала создадим тестовую базу данных и таблицу в ней:

	:::sql
	CREATE DATABASE  `test_nodejs` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
	USE test_nodejs;
	CREATE TABLE  `test_nodejs`.`test` (
	`id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY ,
	`some_text_data` VARCHAR( 255 ) NOT NULL ,
	`some_date` DATE NOT NULL
	) ENGINE = MYISAM ;

Теперь приступим непосредственно к выполнению запросов.

	:::javascript
	var Client = require('mysql').Client,
    client = new Client();
 
	client.user = 'root'; // Устанавливаем логин
	client.password = 'password'; // Устанавливаем пароль
	client.connect(); // Устанавливаем соединение
	client.query('USE test_nodejs'); // Выполняем запрос на выбор БД
	//  Запрос на вставку
	client.query('INSERT INTO test VALUES (NULL, \'Test\', \'03-28-2011\')',function(){ 
	    // Запрос на выборку
	    client.query('SELECT * FROM test', function(error, result, fields){
	        // Если возникла ошибка выбрасываем исключение
	        if (error){
	            throw error;
	        }
	        // выводим результат
	        console.log(fields);
	        console.log(result);
	        // Завершаем соединение
	        client.end();
	    });
	});

Для тех кто уже достаточно освоился в асинхронном программировании
данный код не вызовет трудностей. Для выполнения запросов используется
метод клиента query, который кроме самого запроса принимает
callback-функцию с параметрами error (ошибка, если возникла), result
(массив объектов результата запроса), fields (описание полей из
множества полей результата). В результате выполнения вышеприведённого
кода получим:

	:::text
	node test.js 
	{ id: 
	   { length: 45,
	     received: 45,
	     number: 2,
	     type: 4,
	     catalog: 'def',
	     db: 'test_nodejs',
	     table: 'test',
	     originalTable: 'test',
	     name: 'id',
	     originalName: 'id',
	     charsetNumber: 63,
	     fieldLength: 20,
	     fieldType: 8,
	     flags: 16899,
	     decimals: 0 },
	  some_text_data: 
	   { length: 69,
	     received: 69,
	     number: 3,
	     type: 4,
	     catalog: 'def',
	     db: 'test_nodejs',
	     table: 'test',
	     originalTable: 'test',
	     name: 'some_text_data',
	     originalName: 'some_text_data',
	     charsetNumber: 192,
	     fieldLength: 765,
	     fieldType: 253,
	     flags: 4097,
	     decimals: 0 },
	  some_date: 
	   { length: 59,
	     received: 59,
	     number: 4,
	     type: 4,
	     catalog: 'def',
	     db: 'test_nodejs',
	     table: 'test',
	     originalTable: 'test',
	     name: 'some_date',
	     originalName: 'some_date',
	     charsetNumber: 63,
	     fieldLength: 10,
	     fieldType: 10,
	     flags: 4225,
	     decimals: 0 } }
	[ { id: 1,
	    some_text_data: 'Test',
	    some_date: Invalid Date } ]

На этом всё. Если есть какие-либо вопросы по данной теме, задавайте их в
комментариях ниже, постараюсь ответить.

  [Mysql + Node.js]: /media/2011/03/Mysql-300x76.png
    "Mysql + Node.js"