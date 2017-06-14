Title: Multiple select в PHP
Date: 2012-01-01 21:39
Author: Admin
Category: Другое
Tags: multiple select, PHP
Lang: ru

![php logo][]

Всех с новым годом! Сегодня решил сделать краткую заметку по работе с
multiple select в php. Думаю кому-нибудь пригодится.

Для примера возьмем форму содержащую multiple select:

	:::html
	<form type="post" action="">
	<select name="fruits" multiple>
	    <option value="1">apples</option>
	    <option value="2">oranges</option>
	    <option value="3">bananas</option>
	</select>
	<input type="submit">
	</form>

В таком случае при множественном выделении элементов в обрабатывающий
скрипт будет передаваться только один (последний выделенный) элемент.
Для того чтобы получить все элементы достаточно заменить значение
атрибута name тега select на "fruits[]", тогда в `$_POST['fruits']` будет
массив значений выделенных элементов.

  [php logo]: /media/2012/01/wordpress-e-gli-script-segreti-per-evitare-lu-L-1-300x182.jpg
    "php logo"
