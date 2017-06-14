Title: Очередь сообщений на node.js и memcacheq
Date: 2011-10-07 23:24
Author: Admin
Category: Node.js
Tags: memcacheq, node.js, PHP, очередь сообщений

Привет! Столкнулся с необходимостью использования очередей сообщений в
текущем проекте. Знаю что есть готовые решения, но я все же решил
написать свой небольшой велосипед. Итак, поехали...

Описание
--------

![scheme][]

В поставленной передо мной задаче необходимо выполнять ресурсоемкие
операции (такие как работа с сетью, декодирование mp3-файлов), а также
обращаться к бизнес-логике приложения для потока входных данных.
Приложение написано на php, поэтому очевидно что удобнее всего писать
worker'ы на этом языке в виде cli скриптов. В моем случае это сделать
очень просто, т.к. в проекте используется yii, а в нем есть
замечательная поддержка написания консольных команд при этом можно
использовать весь код бизнес-логики используемый в основном приложении.

Для реализации хранения заданий отличным решением стало memcacheq.
Memcacheq - это сервис поддержки очередей с использованием api
memcached. Подробнее узнать о том что это за зверь можете на [офф.
сайте][]. Стоит отметить что в связи с использованием BerkleyDB в
memcacheq есть ограничение на размер сообщения в очереди, которое
составляет около 64Кб, если для вас этого мало, то стоит подумать о
другом решении.

Также потребуется менеджер очереди, который будет контролировать работу
воркеров (порождать, отслеживать статус выполнения, получать
результаты). Очевидно что менеджер должен работать постоянно и
периодически проверять нет ли новых заданий. Для реализации менеджера я
выбрал Node.js, как мне кажется это очень подходящая технология для этих
целей. В основном выбор пал на node из-за его асинхронности, возможности
легко и быстро написать демон, который будет вписываться в архитектуру
проекта и также на меня повлиял предыдущий опыт работы с данной
технологией, который оставил в основном положительные впечатления.

Реализация
----------

На данном этапе у вас уже должен быть настроен и запущен memcacheq,
установлен nodejs. Также нам понадобиться модуль nodejs под названием
memcached. Установить его можно следующей командой:

    :::bash
    npm install memcached

Основные составляющие части менеджера очереди:

-   Бесконечный цикл опроса очереди на наличие заданий. При этом также в
    цикле должна проводиться проверка на состояние запущенных worker'ов.
    Т.к. мы не можем себе позволить создание worker'ов в таком
    количестве в котором доступны задания, то нам необходимо ввести
    ограничение на количество одновременно обрабатываемых заданий. В
    данном цикле перед созданием новых потоков проверяется наличие
    свободного места, т.е. worker создается только в случае если
    количество текущих worker'ов меньше установленного ограничения.
-   Объект worker'а - представляет из себя оболочку над процессом
    worker'а и хранит его состояние.
-   Создание worker'а - процесс инициализации объекта worker'а на основе
    данных полученных от memcacheq
-   Мониторинг. Для отслеживания состояния выполнения заданий создадим
    web-сервер который будет отвечать информацией о текущем статусе
    выполнения каждого выполняемого worker'а.
-   Т.к. в моя задача связанна с передачей большого объема данных, то
    появилось необходимость ввести поправку на возможную ошибку передачи
    данных. Это подразумевает повторное занесение задания в очередь в
    случае если worker вернет ошибку передачи, которая может быть
    определена проверкой контрольной суммы передаваемых данных.

Теперь собственно исходный код:

    :::javascript
    var util = require('util'),
        exec = require('child_process').exec;

    var http = require('http');
    var Memcached = require('./lib/memcached.js');
    var memcached = new Memcached('127.0.0.1:22201', {maxValue:65000, reconnect:2000, retry:1000, timeout:10000});

    var creating = false;
    var workers_count = 2;
    var transmit_error_retry_count = 3;
    var workers = {};
    var tasks = {};
    var transmit_errors = {};
    var command_line = '/path/to/worker/script';

    // Возможные состояния процесса
    var WORKER_SUCCESS_DONE = 1,
        WORKER_TRANSMIT_ERROR = 2,
        WORKER_CRITICAL_ERROR = 3,
        WORKER_IN_WORKING_PROCESS = 4;

    // Функция выполняемая в бесконечном цикле
    function check_feeds(){
        for (i in workers){
            if (workers[i].status == WORKER_SUCCESS_DONE){
                if (transmit_errors[i] != undefined)
                    delete transmit_errors[i];
                delete workers[i];
                delete tasks[i];
            }else if(workers[i].status == WORKER_TRANSMIT_ERROR){
                if (transmit_errors[i] == undefined)
                    transmit_errors[i] = 1;
                else
                    transmit_errors[i]++;
                if (transmit_errors[i] < transmit_error_retry_count)
                    push_back(tasks[i]);
                else{
                    delete transmit_errors[i];
                    delete tasks[i];
                }
                delete workers[i];
            }else if (workers[i].status != WORKER_IN_WORKING_PROCESS){
                if (transmit_errors[i] != undefined)
                    delete transmit_errors[i];
                delete workers[i];
            }
        }
        
        // Если есть свободные места вызываем функцию
        // создающую worker'ов
        if (!creating && (obj_count(workers) < workers_count))
            create_worker();
    }

    // Возвращение задания в очередь
    function push_back(task){
        memcached.set("tracks", task, 0);
    }

    // Функция выполняющая создание новых worker'ов
    function create_worker(){
        creating = true;
        memcached.get("tracks", function(err, result){
            if (!result)
                creating = false;
            else{
                check_feeds();
                work = JSON.parse(result);
                tasks[work['id']] = work;
                workers[work['id']] = new Worker(work);
                // Если все ещё есть свободные места
                // то делаем рекурсивный вызов
                if (obj_count(workers) < workers_count){
                    create_worker();
                }else{
                    creating = false;
                }
            }
        });
    }

    // Конструктор объекта worker'а
    function Worker(id, data){
        this.status = WORKER_IN_WORKING_PROCESS;
        
        // Здесь можно сформировать 
        // параметры командной строки
        var params;
        
        exec(command_line + params, function(err, data){
            console.log(id, data);
            if (err)
                workers[id].status = WORKER_CRITICAL_ERROR;
            else
                workers[id].status = data;
        })
    }

    setInterval(function(){
        check_feeds();
    }, 100);

    // Monitoring server
    http.createServer(function (req, res) {
        res.writeHead(200, {'Content-Type': 'text/plain'});
        for (i in workers){
            res.write(i +': ' + workers[i].status + "\n");
        }
        // Для того чтобы заработал след. код
        // необходимо внести изменения
        // в модуль memcache (см. ниже)
        memcached.queue(function (err, result){
            res.end('Queue:' + result);
        });
    }).listen(8080, "127.0.0.1");

    // Stuff
    function obj_count(obj){
        var i = 0;
        for (j in obj) i++;
        return i;
    }

Для того чтобы корректно обрабатывать статусы выполнения задания
worker'ы должны возвращать определенные заранее значения. В моем случае
worker может вернуть одно из 3х состояний обозначенных в начале
исходного кода.

Также стоит отметить, что для реализации отображения количества задач в
очереди memcacheq необходимо выполнить запрос stats queue, но модуль
memcached по всей видимости его не поддерживает. По-этому я внес
небольшие дополнения чтобы реализовать данный функционал. Исходный код
модуля доступен [по ссылке][].

In the end..
------------

Стоит заметить, что при помощи подобной организации системы вы сможете
распараллелить ресурсоемкие вычисления. Особенно это удобно, когда вам
необходимо обращаться к бизнес-логике написанной, например, на PHP. В
завершении хочу добавить что полученная система очереди сообщений сильно
направленная на реализацию поставленной передо мной задачи. Но я считаю,
что вы без проблем сможете доработать код для реализации нужного вам
функционала. Спасибо за внимание, буду рад ответить на возникшие
вопросы.

  [scheme]: /media/2011/10/png
  [офф. сайте]: http://memcachedb.org/memcacheq/
  [по ссылке]: http://pastebin.com/MgSFU6Gb
