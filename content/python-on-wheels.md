Title: Python wheels для быстрой установки зависимостей
Date: 2015-01-16 23:30
Author: Admin
Category: Python
Tags: benchmark, innodb, myisam, MySQL, БД

Часто все зависимые python пакеты устанавливаются при помощи pip из PyPI и/или VCS. Такой подход имеет ряд недостатков:

 -  производительность - каждый раз необходима скачивать и собирать пакеты что занимает большое количество времени
 -  работа в оффлайн режиме - без подключения к интернету не получится установить зависимости
 -  стабильность - установка зависимостей невозможна в случае:
     -  неполадок на стороне PyPI
     -  неполадок на стороне VCS (GitHub, Bitbucket, etc)
     -  нарушения зависимостей (удаление репозитория с Github, удаление пакета из PyPI и тд)
     -  неполадок у хостинг провайдера, которые могут привести к недоступности необходимых сетевых ресурсов (PyPI, VSC, etc)

Для решения этой проблемы предлагается использование заранее подготовленных пакетов wheel для всех зависимостей и хранение их в репозитории системы.

Создаем архив wheel пакетов
---------------------------

Wheel - это современный формат распространения пакетов в Python среде, который пришел на замену eggs. Рассмотрим процесс создания архива wheel для всех зависимостей системы. 

Представим типичный Python проект с файлом requirements.txt содержащим зависимости. Пример файла `requirements.txt`:

```
svgwrite==1.1.6
ipython==2.3.0
flask==0.10.1
flask-mongoengine==0.7.1
flask-uploads==0.1.3
-e git://github.com/Samael500/flask-principal.git@dab7f391f0eeb76a25fa1b3dae7308a0924c8a12#egg=flask-principal
-e git://github.com/Samael500/flask-security.git@f1042b5db67147b8ddaa8b767b2dfe063bb56ffa#egg=flask-security
Flask-Admin==1.0.8
Flask-Session==0.1.1
Flask-Script==2.0.5
gunicorn==19.1.1
Flask-Testing==0.4.2
tornado==4.0.2
nose==1.3.4
pep8==1.5.7
Pillow==2.6.1
pyflakes==0.8.1
pylama==6.1.1
spec==0.11.1
py-bcrypt==0.4
WTForms==1.0.4
blessings==1.6
beautifulsoup4==4.3.2
lxml==3.4.1
-e git://github.com/Samael500/jinja-assets-compressor.git@8e1639cec6f8b347794fe1334519daacc6b763b0#egg=jac
PyYAML==3.10
```

В нашем файле `requirements.txt` есть зависимости из внешних ресурсов (не PyPI), которые предполагают загрузку пакетов из VCS (в данном случае из git репозиториев на Github). Скопируем старый `requirements.txt` в `requirements-remote.txt`, а в `requirements.txt` заменим внешние ресурсы на обычные пакеты из PyPI и получим:

```
svgwrite==1.1.6
ipython==2.3.0
flask==0.10.1
flask-mongoengine==0.7.1
flask-uploads==0.1.3
flask-principal
flask-security
Flask-Admin==1.0.8
Flask-Session==0.1.1
Flask-Script==2.0.5
gunicorn==19.1.1
Flask-Testing==0.4.2
tornado==4.0.2
nose==1.3.4
pep8==1.5.7
Pillow==2.6.1
pyflakes==0.8.1
pylama==6.1.1
spec==0.11.1
py-bcrypt==0.4
WTForms==1.0.4
blessings==1.6
beautifulsoup4==4.3.2
lxml==3.4.1
jac
PyYAML==3.10
```

Это делается для того, чтобы при установке из архива wheel пакетов не происходили запросы к внешним VCS, а брались локальные wheel, которые мы сейчас будем генерировать.

Cоздаем и активируем `venv`:
```
pyvenv venv
. venv/bin/activate
```

Устанавливаем все пакеты как обычно, но из `requirements-remote.txt`:
```
pip install -r requirements-remote.txt
```

Сгенерируем архив всех пакетов PyPI, всех их зависимостей и всех зависимостей внешних пакетов (VCS). Для этого нам потребуется свежая версия `pip` и пакет `wheel`:
```
pip install -U pip
pip install wheel
mkdir wheels
pip wheel -w wheels/ -r requirements-remote.txt --pre --allow-all-external
```

После этого получаем архив wheel пакетов для всех зависимостей кроме внешних (VCS). Для внешних пакетов устанавливаемых из исходников необходимо сгенерировать пакеты вручную при помощи `setup.py bdist_wheel`:

```
cd venv/src/flask-principal
python setup.py bdist_wheel --dist-dir ../../../wheels/
cd ../flask-security
python setup.py bdist_wheel --dist-dir ../../../wheels/
cd ../jac
python setup.py bdist_wheel --dist-dir ../../../wheels/
```

Теперь в директории `wheels` есть все необходимые пакеты для установки всех зависимостей системы. Процесс уставновки зависимостей из локального архива пакетов выполняется так:
```
pip install --no-index -f wheels/ -r requirements.txt
```
обратите внимание, что используется файл `requirements.txt`, а не `requirements-remote.txt`.

Тестирование скорости установки
------------------------------------------

Обычная установка со скачиванием пакетов из PyPI и VCS:
```
time pip install -r requirements-remote.txt
real    4m20.655s
user    1m31.242s
sys 0m55.539s
```

Установка из локального архива wheels:
```
time pip install --no-index -f wheels/ -r requirements.txt
real    1m3.412s
user    0m4.808s
sys 0m31.210s
```

Из результатов можно сделать вывод, что время установки пакетов из локального архива в нашем случае меньше в 4 раза.
Что логично, т.к. пакеты заново не скачиваются из интернета и не компилируются.

Бонус
-------

Для удобства написал [небольшой скрипт](https://gist.github.com/dizballanze/070434f4eb3b5febae39), автоматизирующий сборку пакетов установленных из исходников.

Пример использования скрипта:
```
python build_wheels --sources-dir venv/src/ --wheels-dir wheels/
```

Скрипт пройдется по всем поддиректориям `venv/src/` и в каждой из них попробует собрать пакет в директорию `wheels/`.