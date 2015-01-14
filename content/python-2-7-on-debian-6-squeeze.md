Title: Python 2.7 в Debian 6 Squeeze
Date: 2012-07-22 09:26
Author: Admin
Category: Python
Tags: python, virtualenv

![python logo][]

Приветствую! На данный момент в stable репозитарии Debian squeeze лежит
python 2.6.6. Однако, последней (на момент написания поста) стабильной
версией ветки 2.x является 2.7.3. Далее рассмотрим, как установить
несколько версий python и использовать их независимо.

Устанавливаем Python 2.7.3
--------------------------

Скомпилируем python 2.7.3 из исходников. Стянуть последнюю версию можно
[здесь][].

	:::bash
	cd /tmp
	wget http://www.python.org/ftp/python/2.7.3/Python-2.7.3.tgz
	tar xvzf Python-2.7.3.tgz
	cd Python-2.7.3
	./configure --prefix=/usr/local/python-2.7.3
	make && make install
	ln -s /usr/local/python-2.7.3/bin/python2.7 /usr/bin/python2.7.3

После этого можем проверить что все работает:

	:::bash
	python2.7.3 
	Python 2.7.3 (default, Jul 22 2012, 10:05:02) 
	[GCC 4.4.5] on linux2
	Type "help", "copyright", "credits" or "license" for more information.
	>>>

Используем virtualenv
---------------------

Для того чтобы обеспечить удобную работу с несколькими версиями python
воспользуемся утилитой virtualenv. Сначала скачиваем скрипт:

	:::bash
	cd /home/dizballanze
	mkdir apps
	cd apps
	wget https://raw.github.com/pypa/virtualenv/master/virtualenv.py

Теперь нам нужно выполнить скрипт с использованием нужной версии python:

	:::bash
	mkdir test_app
	cd test_app
	python2.7.3 ../virtualenv.py venv

Таким образом мы успешно добавили виртуальное окружение. В текущей
директории должна появится директория с названием venv (второй
параметр). Для того чтобы активировать окружение выполните:

	:::bash
	source venv/bin/activate

Сразу после этого должна изменится строка ввода в терминале следующим
образом:

	:::bash
	(venv)dizballanze@dizballanze-desktop:~/apps/test

Что означает, что мы находимся в окружении с названием venv. Проверим
версию python:

	:::bash
	python --version
	Python 2.7.3

Таким образом можно установить любое количество версий Python на одной
машине и при этом использовать их независимо. Более того, активировав
virtualenv все устанавливаемые через pip пакеты будут хранится в
директории с файлами venv и не будут взаимодействовать с другими
проектами, которые находятся в других окружениях.

  [python logo]: /media/2012/07/python-logo-master-v3-TM.png
    "python logo"
  [здесь]: http://www.python.org/download/releases/
