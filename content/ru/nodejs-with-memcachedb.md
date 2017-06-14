Title: Хранилища данных в Node.JS. Memcachedb
Date: 2011-07-02 23:04
Author: Admin
Category: Node.js
Tags: memcachedb, node.js
Lang: ru

![MemcacheDB][]

Сегодня я расскажу, как начать работать с MemcacheDB в Node.JS.

Memcachedb
----------

Memcachedb - это key-value база данных, основанная на memcached. Для
тех, кто работал с memcached, начало работы с memcachedb не будет
требовать особых усилий, т.к. они используют общее API. Основные
возможности Memcachedb:

-   Распределенное хранилище пар ключ-значение
-   В отличие от memcached не является решением для кеширования, т.к.
    хранит данные на диске
-   В качестве движка хранилища используется Berkeley DB
-   Поддержка транзакций
-   Поддержка репликации
-   Api memcachedb включает следующие команды:

    -   get - получения значения по ключу или нескольким ключам
    -   set, add, replace - установка значения, сохранения значения
        только в случае если оно не было установлено ранее и установка
        значения только если оно было установлено ранее
    -   append / prepend - добавление данных в после существующего
        значения или перед ним
    -   incr / decr - инкремент, декремент значения
    -   delete - удаление значения
    -   stats - получение статистической информации

Установка модуля memcached
--------------------------

Как я уже упоминал memcacheDB имеет такое же API, как и у memcached
(кроме небольших изменений, например записи не удаляются по истечении
срока), поэтому мы будем использовать модуль предназначенный для работы
с memcached. Модуль имеет название memcached и доступен для установки
через npm:

    :::bash
    npm install memcached

Я подразумеваю, что вы уже установили и запустили memcacheDB, если нет,
то вам [сюда][]. После установки модуля, мы сразу можем начать
использовать его в наших программах на node.js. Попробуем подключится к
БД:

    :::javascript
    var Memcached = require('memcached');
    var memcached = new Memcached('127.0.0.1:21201');

Пишем Hello World
-----------------

Напишем скрипт, который сначала запишет значение в БД и затем считает
его и выведет в консоль:

    :::javascript
    var Memcached = require('memcached');
    var memcachedb = new Memcached('127.0.0.1:21201');
    memcachedb.set("test", "Hello world", 0, function(){
        memcachedb.get("test", function(err, result){
            if (err) throw err;
            console.log(result); // Hello world
        });
    });

Подробную информацию по функциям api можете получить [здесь][] и в
[примерах][].

На этом все. До новых постов!

  [MemcacheDB]: /media/2011/07/Снимок-300x204.png
  [сюда]: http://memcachedb.googlecode.com/svn/trunk/INSTALL
  [здесь]: https://github.com/3rd-Eden/node-memcached/blob/v0.0.1/README.md
  [примерах]: https://github.com/3rd-Eden/node-memcached/tree/v0.0.1/examples
