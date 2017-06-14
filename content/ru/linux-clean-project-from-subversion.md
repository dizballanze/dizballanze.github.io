Title: Очистка проекта от служебных файлов subversion
Slug: ochistka-proekta-ot-sluzhebnykh-failov-subversion
Date: 2011-06-07 20:32
Author: Admin
Category: Linux
Lang: ru
Tags: Linux, svn

![subversion][]

Если вы используете svn, то при переносе проекта на хостинг вам
понадобится очистить дерево проекта от служебных файлов. SVN сохраняет
свои служебные файлы в директориях .svn по всему проекту. Для того чтобы
удалить все директории .svn нужно выполнить следующие команды:

	:::bash
	cd /var/www/projectfind . -name .svn -exec rm -R {} \; -print

Я рекомендую выполнять удаление служебных файлов из копии проекта, если
вы не уверены на 100% что не будете использовать svn в дальнейшем.

  [subversion]: /media/2011/06/subversion_logo_hor-468x64.png
    "subversion"
