Title: MySQL - обзор типов таблиц
Date: 2011-01-29 18:42
Author: Admin
Category: БД
Tags: benchmark, innodb, myisam, MySQL, БД

![mysql][]

Здравствуйте, сегодня мы поговорим о типах таблиц в MySQL. Архитектура
MySQL позволяет подключать разные движки таблиц. На данный момент MySQL
поддерживает множество различных типов таблиц, каждый из которых имеет
свои преимущества и недостатки. Я перечислю и коротко опишу основные
типы таблиц, а затем проведу небольшой тест производительности наиболее
часто используемых типов - myisam и innodb.

Для того что-бы посмотреть какие типы поддерживает ваша инсталляция
MySQL необходимо выполнить следующий SQL запрос:

    :::sql
    SHOW ENGINES;

В результате вы получаете таблицу содержащую информацию о том какие типы
таблиц установлены в вашей системе и краткое описание их возможностей.

Engine             | Support | Comment | Transactions | XA   | Savepoints
:------------------|:--------|:--------|:-------------|:-----|:-----------
FEDERATED          | NO      | Federated MySQL storage engine | NULL         | NULL | NULL CSV                | YES     | CSV storage engine                                             | NO           | NO   | NO         
MyISAM             | YES     | MyISAM storage engine                                          | NO           | NO   | NO         
BLACKHOLE          | YES     | /dev/null storage engine (anything you write to it disappears) | NO           | NO   | NO         
MRG_MYISAM         | YES     | Collection of identical MyISAM tables                          | NO           | NO   | NO         
MEMORY             | YES     | Hash based, stored in memory, useful for temporary tables      | NO           | NO   | NO         
ARCHIVE            | YES     | Archive storage engine                                         | NO           | NO   | NO         
InnoDB             | DEFAULT | Supports transactions, row-level locking, and foreign keys     | YES          | YES  | YES        
PERFORMANCE_SCHEMA | YES     | Performance Schema                                             | NO           | NO   | NO

Нас в основном будет интересовать столбец support, который содержит
информацию о поддержке типа таблицы и может принимать значения: NO - не
поддерживается, YES - поддерживается, DEFAULT -используется
по-умолчанию. Начиная с версии 5.5.5 по-умолчанию выбран тип innodb,
ранее стандартным типом был myisam.

В версии MySQL 5.5 поддерживается 9 различных типов таблиц.

-   **InnoDB** - движок с поддержкой транзакций, откатов и защитой от
    потери данных. В данном типе таблиц используются блокировки на
    уровне записи и не блокирующее чтение, что позволило улучшить
    производительность при многопользовательском режиме работы. InnoDB
    сохраняет пользовательские данные в кластерных индексах, что
    позволяет компенсировать в/в для простых запросов основанных на
    первичных ключах.
-   **MyISAM** - движок таблиц MySQL используемый в основном в
    Web-приложениях, хранилищах данных и других программных средах.
    Данный тип таблиц поддерживается всеми инсталляциями MySQL.
-   **Memory** - хранит данные в оперативной памяти для очень быстрого
    доступа. Также известен как HEAP (куча).
-   **Merge** - используется для логического объединения одинаковых
    MyISAM таблиц и обращение к ним, как к единому объекту. Хорошо
    подойдет для очень больших хранилищ данных.
-   **Archive** - идеальное решение для хранения больших объёмов
    информации, к которой не требуется частый доступ.
-   **Federated** - предоставляет возможность объединять различные MySQL
    сервера для создания одной логической базы данных из нескольких
    физических машин. Идеально подойдет для архитектур, которые
    поддерживают распределенное хранение данных.
-   **CSV** - хранит пользовательские данные в текстовых файлах разделяя
    значения запятыми. Используется если необходим простой обмен с
    приложениями, которые умеют экспортировать/импортировать данные из
    CSV формата.
-   **Blackhole** - принимает, но не возвращает никаких данных.
    Результатами любых запросов из таких хранилищ будут пустые выборки.
-   **Example** - тестовый движок, не выполняет никаких функций, будет
    полезен только разработчикам, которые собираются писать свой движок,
    в качестве примера.

Сравнительная таблица основных типов таблиц

Функция | MyISAM | Memory | InnoDB | Archive
:-------|:-------|:-------|:-------|:-------
Максимальный объём хранимых данных | 256TB | RAM | 64TB | Нет
Транзакции | Нет | Нет | Да | Нет
Блокировки | Таблица | Таблица | Запись | Запись
MVCC | Нет | Нет | Да | Нет
B-деревья | Да | Да | Да | Нет
Хэш индексы | Нет | Да | Нет | Нет
Индексы полнотекстового поиска | Да | Нет | Нет | Нет
Кластерные индексы | Нет | Нет | Да | Нет
Кэширование данных | Нет | Н/д | Да | Нет
Кэширование индексов | Да | Н/д | Да | Нет
Сжатие данных | Да | Нет | Да | Да
Шифрование данных | Да | Да | Да | Да
Поддержка кластерных БД | Нет | Нет | Нет | Нет
Репликация | Да | Да | Да | Да
Внешние ключи | Нет | Нет | Да | Нет
Бэкап | Да | Да | Да | Да
Кэширование запросов | Да | Да | Да | Да

Тестирование производительность InnoDB и MyIASM
-----------------------------------------------

Наибольший интерес для web-разработчика составляют innodb и myisam.
Сейчас мы проведем сравнительный тест производительности этих типов
таблиц. Для этого сначала создадим две одинаковые по структуре таблицы,
но с разным типом движка хранения:

    :::sql
    CREATE TABLE `inno` (
      `id` BIGINT(20) NOT NULL AUTO_INCREMENT,
      `data` VARCHAR(255) NOT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB;
     
    CREATE TABLE `myisam` (
      `id` BIGINT(20) NOT NULL AUTO_INCREMENT,
      `data` VARCHAR(255) NOT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=MyISAM;

Напишем небольшой скрипт который будет выполнять 3 теста: запись данных
(insert), выборка по ключу, выборка по не ключевому полю.

    :::php
    <?php
    // ...
    class timer{
        public $value=0;
 
        public function start(){
            $this->value = microtime(true);
        }
 
        public function end(){
            return microtime(true) - $this->value;
        }
    }
 
    $timer = new timer();
 
    mysql_connect('localhost','root');
    mysql_select_db('test');
 
    $data = array();
    $select_query = 'SELECT data FROM myisam WHERE id = :val:';
    for ($i = 0; $i <= 10000; $i++){
        $result = mysql_query(str_replace(':val:', $i, $select_query));
        $tmp = mysql_fetch_array($result);
        $data[] = $tmp[0];
    }
 
    echo '<br/>MyISAM select<br/>';
    $select_query = 'SELECT * FROM myisam WHERE data = :val:';
    $timer->start();
    foreach ($data as $one){
        mysql_query(str_replace(':val:', $one, $select_query));
    }
    echo $timer->end() . ' s<br/>';
 
    echo '<br/>InnoDB select<br/>';
    $select_query = 'SELECT * FROM inno WHERE data = :val:';
    $timer->start();
    foreach ($data as $one){
        mysql_query(str_replace(':val:', $one, $select_query));
    }
    echo $timer->end() . ' s<br/>';
 
    /*
 
    $data = array();
    for ($i = 0; $i <= 10000; $i++){
        $data[] = mt_rand(0, 100500);
    }
 
    echo '<br/>MyISAM select by key<br/>';
    $select_query = 'SELECT * FROM myisam WHERE id = :val:';
    $timer->start();
    for ($i = 0; $i <= 10000; $i++){
        mysql_query(str_replace(':val:', $i, $select_query));
    }
    echo $timer->end() . ' s<br/>';
 
    echo '<br/>InnoDB select by key<br/>';
    $select_query = 'SELECT * FROM inno WHERE id = :val:';
    $timer->start();
    for ($i = 0; $i <= 10000; $i++){
        mysql_query(str_replace(':val:', $i, $select_query));
    }
    echo $timer->end() . ' s<br/>';
    */
 
    /*
 
    $data = array();
    for ($i = 0; $i <= 10000; $i++){
        $data[] = mt_rand(0, 100500);
    }
 
    echo '<br/>MyISAM insert<br/>';
    $insert_query = 'INSERT INTO myisam VALUES (NULL,\':val:\')';
    $timer->start();
    foreach ($data as $one){
        mysql_query(str_replace(':val:', $one, $insert_query));
    }
    echo $timer->end() . ' s<br/>';
 
    echo 'InnoDB insert<br/>';
    $insert_query = 'INSERT INTO inno VALUES (NULL,\':val:\')';
    $timer->start();
    foreach ($data as $one){
        mysql_query(str_replace(':val:', $one, $insert_query));
    }
    echo $timer->end() . ' s<br/>';
     */

Для того что-бы выполнить тест, нужно раскоментить один соответствующий
блок кода. И собственно, то что у меня получилось в результате
тестирования:

Тест                         | InnoDB    | MyISAM
:----------------------------|:----------|:--------
Вставка данных(insert)       | 15.697 с  | 1.591 с
Выборка по ключу             | 1.678 с   | 1.603 с
Выборка по не ключевому полю | 149.961 c | 95.984 c

Как мы видим myisam работает значительно быстрее, особенно это заметно
при вставке данных. Хотя innodb и дает ряд новых возможностей и
преимуществ, такая медлительность не позволяет ему конкурировать с
myisam, особенно в web-приложениях.

  [mysql]: /media/2011/01/mysql-125x125.png
    "MySQL logo"