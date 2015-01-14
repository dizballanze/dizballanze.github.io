Title: Быстрое добавление виртуальных хостов Apache в Ubuntu/Debian
Date: 2011-05-31 17:51
Author: Admin
Category: Linux
Tags: apache, debian, hosts, Linux, администрирование

![apache][]

Если вы web-разработчик, который работает сразу над несколькими
проектами, то вам может показаться не удобным использование localhost и
под-директорий для разграничения проектов. Кроме того такой подход
иногда не позволяет приблизится к боевому окружению, когда сайт висит на
отдельном хосте. Поэтому удобно было бы создавать отдельный виртуальный
хост для каждого разрабатываемого проекта, который будет доступен по
удобному адресу. Сейчас мы рассмотрим как произвести быстрое добавление
виртуального хоста в ОС Linux. Я как всегда буду рассматривать настройку
на примере Debian Linux, но я думаю, что процесс не будет очень сильно
отличаться для других дистрибутивов.

Создание виртуального хоста
---------------------------

Для начала необходимо скопировать стандартный файл конфигурации хоста в
apache. Мы будем использовать его в качестве основы для настройки новых
хостов:

	:::bash
	cd /etc/apache2/sites-available/
	cp default test

Откроем файл test в любом текстовом редакторе и уведем приблизительно
следующее:

	:::apache
 	<VirtualHost *:80>
		ServerAdmin webmaster@localhost
		DocumentRoot /var/www
		<Directory />
			Options FollowSymLinks
			AllowOverride All
		</Directory>
		<Directory /var/www/>
			Options Indexes FollowSymLinks MultiViews
			AllowOverride All
			Order allow,deny
			allow from all
		</Directory>
		ErrorLog ${APACHE_LOG_DIR}/error.log
		LogLevel warn
		CustomLog ${APACHE_LOG_DIR}/access.log combined
	</VirtualHost>

Итак, допустим нам нужно настроить хост с корнем в директории
/var/www/test/ в таком случае изменим файл конфигураций следующим
образом:

	:::apache
	<VirtualHost 127.0.1.1:80>
		ServerAdmin webmaster@localhost
		DocumentRoot /var/www/test
		<Directory />
			Options FollowSymLinks
			AllowOverride All
		</Directory>
		<Directory /var/www/>
			Options Indexes FollowSymLinks MultiViews
			AllowOverride All
			Order allow,deny
			allow from all
		</Directory>
		ErrorLog ${APACHE_LOG_DIR}/error.log
		LogLevel warn
		CustomLog ${APACHE_LOG_DIR}/access.log combined
	</VirtualHost>

С конфигурацией apache мы закончили, теперь нужно создать символическую
ссылку на наш файл конфигураций в директории /etc/apache2/sites-enabled/
для этого выполним следующую команду:

	:::bash
    ln -s /etc/apache2/sites-available/test /etc/apache2/sites-enabled/test 

или
	
	:::bash
	a2ensite test

Создание символического имени
-----------------------------

Т.к. в начале мы указали адрес 127.0.1.1 теперь необходимо связать его с
символическим именем добавив следующую строку в файл /etc/hosts:

	:::text
	127.0.1.1  test.loc

На этом все настройки закончены, можно выполнить перезапуск apache:

	:::bash
	/etc/init.d/apache2 restart

Теперь вы можете открыть в браузере http://test.loc или 127.0.1.1 и
увидеть то что находится в директории /var/www/test. Таким образом вы
можете настроить столько хостов, сколько вам нужно, главное выбирать для
каждого из них свой ip-адрес и символическое имя.

Бонус
-----

Для тех кто работает с Zend Framework полезным будет настройка хоста с
корнем в директории public. Для этого очевидно нужно просто изменить
путь после DocumentRoot на путь к проекту включающий /public.

UPD
---

Более простой способ:

	:::apache
	<VirtualHost *:80>
	   DocumentRoot "/var/www/skeleton/public"
	   ServerName skeleton.local
	   # This should be omitted in the production environment
	   SetEnv APPLICATION_ENV development
	   <Directory "/var/www/skeleton/public">
	       Options Indexes MultiViews FollowSymLinks
	       AllowOverride All
	       Order allow,deny
	       Allow from all
	   </Directory>
	</VirtualHost>

После этого добавляем в /etc/hosts:

	:::text
	127.0.0.1 skeleton.local

Включаем хост и рестартим апач:

	:::bash
	a2ensite skeleton# /etc/init.d/apache2 restart

  [apache]: /media/2011/05/feather.gif
    "apache"
    