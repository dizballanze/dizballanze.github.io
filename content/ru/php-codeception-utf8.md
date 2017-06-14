Title: Codeception проблема с русскими символами в utf-8
Date: 2012-02-29 13:57
Author: Admin
Category: Другое
Tags: acceptance, codeception, testing, utf-8

Разбираюсь с [codeception][]. В acceptance тестах возникла проблема с
распознаванием русских символов в utf-8:

	:::php
	<?php
	$I = new WebGuy($scenario);
	 
	$I->wantTo('see right title');
	$I->amOnPage('/');
	$I->see('Заголовок на русском');

При этом тест фейлится, хотя логах можно увидеть, что заголовок
установлен правильно. Для решения этой проблемы необходимо установить
следующий meta-тэг:

	:::html
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" >

Только после этого у меня получилось заставить тест показать зелёный
цвет. Другие способы установки кодировки не сработали (ни через php, ни
через apache), хотя при просмотре заголовков кодировка была установлена
в utf-8. Видимо это какая-то особенность Goutte Web Scrapper'а, который
используется в модуле PHPBrowser.

  [codeception]: http://codeception.com/
