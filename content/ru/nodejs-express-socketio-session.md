Title: Используем сессию express в socket.io
Date: 2013-04-19 13:33
Author: Admin
Category: Node.js
Tags: node.js, express, socket.io
Lang: ru


При разработке приложения с использованием socket.io + express часто возникает задача использования сессии express в socket.io. Рассмотрим, как можно решить эту задачу.

Используемые пакеты
-------------------
Нам нужно установить несколько пакетов, которые пригодятся для решения поставленной задачи (предполагается что express и soket.io уже установлены):

```bash
npm install cookie express-session-mongo
```

-  `cookie` - модуль для удобного парсинга cookie
-  `express-session-mongo` - back-end для хранения сессий express в MongoDB

Настраиваем express
-------------------

Настроим сессии в express:

```javascript
var DB = {
  'ip': '127.0.0.1',
  'port': 27017,
  'db': 'test'
}

var	MongoSessionStore = require('express-session-mongo')
  , session_storage = new MongoSessionStore(DB);

var app = express();

app.configure(function(){

  /* .... */

  app.use(express.cookieParser('secret'));
  app.use(express.session({
    store: session_storage,
    secret: 'secret',
    key: 'sid'
  }));
});
```

В данном примере мы используем MongoDB для хранения сессий, но данный приём будет работать и для других хранилищ.

Получаем сессионные данные в soket.io
-------------------------------------

```javascript
// Запускаем web-сервер
var server = http.createServer(app).listen(app.get('port'), function(){
  console.log("Express server listening on port " + app.get('port'));
});

var io = socketio.listen(server);

// Настраиваем socket.io
io.configure(function() {

  // Аутентификация пользователей
  io.set('authorization', function (data, accept) {
    // Проверяем переданы ли cookie
    if (!data.headers.cookie) 
      return accept('No cookie transmitted.', false);

    // Парсим cookie
    data.cookie = cookie.parse(data.headers.cookie);
    
    // Получаем идентификатор сессии
    var sid = data.cookie['sid'];
    
    if (!sid) {
      accept(null, false);
    }

    sid = sid.substr(2).split('.');
    sid = sid[0];
    data.sessionID = sid;

    // Добавляем метод для чтения сессии
    // в handshakeData
    data.getSession = function(cb) {
      // Запрашиваем сессию из хранилища
      session_storage.get(sid, function(err, session) {
        if (err || !session) {
          console.log(err);
          accept(err, false);
          return;
        }
        cb(err, session);
      });
    }
    accept(null, true);
  });
});


// Пример использования
io.sockets.on('connection', function(socket) {
  socket.join('chat');

  socket.on('message', function(data) {
    socket.handshake.getSession(function(err, session) {
      data['user'] = session.name || 'guest';
      io.sockets.in('chat').emit('message', data);
    });
  });
});
```

Для чтения сессии в обработчиках socket.io нужно использовать `socket.handshake.getSession`.

Заключение
----------
Стоит отметить, что если socket.io у вас слушает другой хост/порт, отличный от express, то необходимо предусмотреть другой способ передачи идентификатора сессии.

Полный пример можно посмотреть на [GitHub](https://github.com/dizballanze/express-socketio-session-example/).