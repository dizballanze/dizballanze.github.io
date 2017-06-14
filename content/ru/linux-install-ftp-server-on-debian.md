Title: Ставим FTP-сервер в Debian
Date: 2011-01-03 00:42
Author: Admin
Category: Linux
Tags: debian, ftp, ftpd, администрирование
Lang: ru

![image][]

По просьбе моего друга рассматриваю установку ftp-сервера в Linux.

Начнем с того что установим демон ftpd. Т.к. я использую Debian, то
устанавливать будем при помощи apt-get:
    
    :::bash
    apt-get install ftpd

Итак, поставили, теперь проверяем запущен или нет:

    :::bash
    ps aux | grep ftp

В моём случае не запущен, значит запускаем:

    :::bash
    /etc/init.d/ftpd start
    bash: /etc/init.d/ftpd: Нет такого файла или каталога

Хмм...

    :::bash
    whereis ftpd
    ftpd:

Так, что-то непонятное. При всём этом man ftpd выдаёт страницу
руководства. Пробуем перезагрузится...После перезагрузки ps не выдаёт
никакого результата при поиске слова ftpd также и whereis. Но проверив
свой хост nmap'ом я увидел следующее:

    :::bash
    nmap 127.0.0.1
     
    Starting Nmap 4.62 ( http://nmap.org ) at 2011-01-02 23:37 EET
    Interesting ports on localhost (127.0.0.1):
    Not shown: 1708 closed ports
    PORT     STATE SERVICE
    21/tcp   open  ftp
    25/tcp   open  smtp
    80/tcp   open  http
    111/tcp  open  rpcbind
    631/tcp  open  ipp
    2049/tcp open  nfs
    3306/tcp open  mysql
     
    Nmap done: 1 IP address (1 host up) scanned in 0.098 seconds

Как мы видим 21 порт открыт и на нём висит ftp-сервер. Бегло просмотрев
man ftpd разобрался с файлами конфигураций. Итак, смотрим что к чему:

-   `/etc/ftpusers` - список пользователей которым запрещён доступ к ftp.
    Формат файла прост, как рубанок - каждая новая строка имя
    пользователя, которому нужно обрезать доступ к питательному вымени
    file transfer protocol :)
-   `/etc/ftpchroot` - список пользователей для которых текущая директория
    должна быть установлена в "искусственный" корень при помощи "chroot"
    перед началом работы.
-   `/etc/ftpwelcome` - приветственное сообщение
-   `/etc/motd` - сообщение после авторизации

Оказалось всё довольно просто. Пробуем залогинится:

    :::bash
    ftp 127.0.0.1
    Connected to 127.0.0.1.
    220 dizballanze-laptop FTP server (Version 6.4/OpenBSD/Linux-ftpd-0.17) ready.
    Name (127.0.0.1:root): dizballanze
    331 Password required for dizballanze.
    Password:
    230- Linux dizballanze-laptop 2.6.26-2-686 #1 SMP Sat Dec 26 09:01:51 UTC 2009 i686
    230- 
    230- The programs included with the Debian GNU/Linux system are free software;
    230- the exact distribution terms for each program are described in the
    230- individual files in /usr/share/doc/*/copyright.
    230- 
    230- Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
    230- permitted by applicable law.
    230 User dizballanze logged in.
    Remote system type is UNIX.
    Using binary mode to transfer files.
    ftp> pwd
    257 "/home/dizballanze" is current directory.

Авторизация прошла успешно и я сразу получил доступ к файловой системе
от пользователя dizballanze без каких-либо дополнительных настроек.
Единственная проблема - это некорректное отображения русских надписей в
терминальном клиенте, но в gFTP всё отображается отлично. Советую
использовать именно его в качестве клиента. Подводя итоги перечислим 5
правил аутентификации ftpd:

1.  Логин должен находится в базе паролей системы - `/etc/passwd` и не
    должен быть равен null.
2.  Логин не должен встречаться в `/etc/ftpusers`
3.  Пользователь должен иметь стандартный интерпретатор команд
    возвращаемый `getusershell`
4.  Если имя пользователя встречается в `/etc/ftpchroot` сессионный корень
    будет изменён на директорию входа при помощи chroot, как для
    "anonymous" или "ftp" аккаунта. Но тем не менее всёравно требуется
    пароль. Данная функция - это промежуточный этап между полностью
    анонимным и полностью привилегированным аккаунтом.
5.  Если имя пользователя "anonymous" или "ftp", то анонимный
    ftp-аккаунт должен быть представлен в файле паролей (пользователь
    "ftp"). В таком случае пользователь получает возможность
    авторизироваться используя любой пароль (по соглашению принято
    использовать email в качестве пароля).

FTPd предоставляет простой способ удалённого доступа к системе без траты
времени на конфигурирование системы. Очень удобно использовать свои
данные для удалённой авторизации. Но при этом стоит учитывать опасность,
которая возникает, т.к. теперь любой пользователь сможет получить доступ
к файлам узнав ваши логин и пароль, к тому же зачастую пароли для
пользователей на локальных машинах далеки от безопасных (по себе знаю).
Так что если вы планируете использовать FTPd советую изменить пароли на
безопасные или заблокировать аккаунты путём добавления их в
/etc/ftpusers. Спасибо за внимание! Да прибудет с вами сила :) !

  [image]: /media/2011/01/ftp_client.png
    "ftp_client"
