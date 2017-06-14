Title: Применение Nginx + Lua для обработки контактной формы
Slug: primenenie-nginx-lua-dlia-obrabotki-prostykh-form
Date: 2015-06-08 18:25
Author: Admin
Category: Другое
Tags: http, nginx, lua

![lua][]

Бывает, что нужно развернуть простой, почти полностью статический сайт. И все что мешает ограничится одним Nginx - это 
простая контактная форма, которая должна только отправлять полученные данные по почте. Конечно можно прикрутить стороннее 
решение, вроде Google Forms, но такие сторонние решения не всегда хорошо кастомизируются. Разворачивать какой-то свой бекенд 
отдельно тоже не очень хочется, придется следить за тем, чтобы он всегда был запущен, усложняется деплой и тд.

Возможным решением  будет использовать nginx модуль [ngx_lua](http://wiki.nginx.org/HttpLuaModule) и использовать 
встраиваемый lua в Nginx. Это позволит нам ограничится Nginx и при этом реализовать кастомный обработчик формы прямо в 
конфиге Nginx, который будет работать эффективно и который проще поддерживать чем отдельный бекенд.

> Пару слов о Lua. Простой, скриптовый язык, чем-то напоминает javascript, но с более мощными конструкциями и без многих 
недостатоков последнего. Хорошо зарекомендовал себя, как встраиваемый язык, из-за удобства встраивания и высокой скорости 
исполнения. Широко применяется в gamedev (напр. используется в WoW).

Установка
---------

Нам понадобится установить несколько пакетов (в примерах показывается для debian/ubuntu систем):

 -  nginx-extras - пакет содержащий Nginx с кучей предустановленных модулей (в том числе ngx_lua)
 -  lua5.1 - интерпретатор lua, просто для того, чтобы можно было что-то проверить в REPL (для ngx_lua он не нужен)
 -  luarocks - менеджер модулей lua
 -  git-core - для того, чтобы установить smtp модуль из GitHub

```
apt-get install nginx-extras lua5.1 luarocks git-core
```

Теперь воспользуемся luarocks для установки модуля [lua-resty-smtp](https://github.com/duhoobo/lua-resty-smtp):

```
sudo luarocks install https://raw.githubusercontent.com/duhoobo/lua-resty-smtp/master/rockspec/resty.smtp-0.0.3-1.rockspec
```

Вобщем-то это все, можно приступать к разработке.

0: Hello world
--------------

Сначала напишем классический hello world пример:

```nginx
server {
    listen    80;

    location /hi {
        content_by_lua '
            ngx.header["Content-Type"] = "text/plain;charset=utf-8"
            ngx.say("Hello world!");
        ';
    }
}
```

После перезапуска проверяем:

```
➜  ~  curl http://10.1.1.97/hi
Hello world!
```

Для обработки запроса мы используем директиву `content_by_lua`, которая принимает строку lua кода и ожидает, что этот код 
сгенерирует и вернет ответ используя Nginx API. Встраивать lua код в конфиг Nginx не обязательно, вместо этого можно использовать 
директиву `content_by_lua_file`.

Nginx предоставляет [полнофункциональный API](http://wiki.nginx.org/HttpLuaModule#Nginx_API_for_Lua) с методами на все 
случаи жизни. Все методы, с которыми мы будем работать в примерах данного поста, предоставляются через модуль `ngx`, 
который автоматически становится доступен нашим lua скриптам при запуске в Nginx.

1: SMTP
-------

Теперь попробуем выполнить отправку какого-либо тестового письма, просто чтобы убедиться, что это работает. Для отправки 
письма будем использовать установленную нами ранее библиотеку lua-resty-smtp. Примерный код скрипта отправка письма через
внешний SMTP будет выглядить так (используем [debugmail.io](https://debugmail.io/) для тестирования):

```lua
-- Загружаем библиотеку для работы с SMTP
local smtp = require("resty.smtp")

from = "<test@example.org>"
to = "<rcpt@example.org>"

-- Формируем данные письма
mesgt = {
    headers = {
        to = to,
        from = from,
        subject = "Mail from Nginx and Lua"
    },
    body = "Hello from Nginx and Lua!"
}

source = smtp.message(mesgt)
-- Выполняем отправку письма
res, error = smtp.send{
    from = from,
    rcpt = to,
    source = source,
    user = "dizballanze@gmail.com",
    password = "<wow-very-secret>",
    server = "debugmail.io",
    port = 25
}

-- Формируем ответ сервера
ngx.header["Content-Type"] = "text/plain;charset=utf-8"
if res then
    ngx.say("Success!")
else
    -- Статус 500 в случае ошибки
    ngx.status = ngx.HTTP_INTERNAL_SERVER_ERROR
    ngx.say("Error while send mail")
    ngx.say(error)
end
```

Размещаем этот код в директиве `content_by_lua` (или через внешний файл в `content_by_lua_file`) в
 и добавляем директиву resolver, чтобы nginx мог определить ip адрес debugmail.io:

```
server {
    listen 80;

    location /send-mail {
        resolver 8.8.8.8;
        content_by_lua '...';
    }
}
```

Проверяем:

```
➜  ~  curl http://10.1.1.97/send-mail
Success!
```

Проверяем, что письмо пришло и содержит корректные данные на [debugmail (смотреть письмо)](http://bit.ly/1FNrev5).

Меняем пароль на неправильный и проверяем, выводится ли ошибка (не забываем перезапускать Nginx после изменений):

```
➜  ~  curl http://10.1.1.97/send-mail
Error while send mail
535 5.7.0 Invalid login or password
```


2: Form Handling
----------------

Для того, чтобы обработать обычную форму нужно добавить директиву `lua_need_request_body on;`, чтобы 
Nginx подготовил для нас тело запроса и lua мог его распарсить. Далее мы используем метод `ngx.req.get_post_args`, который возвращает таблицу содержащую все параметры запроса.

Дальше дело техники, при помощи `string.format` формируем тело письма и отправляем также, как мы делали 
это в предыдущем примере.


Заключение
----------

Полный пример обработчика формы с настроенным Vagrant, который можно легко запустить самому и потыкать, 
можно найти на [гитхаб](https://github.com/dizballanze/nginx-lua-contact).


  [lua]: /media/2015/6/lua.jpg