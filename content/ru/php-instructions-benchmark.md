Title: Тестируем производительность конструкций языка PHP
Date: 2011-03-13 14:18
Author: Admin
Category: Другое
Tags: benchmark, PHP
Lang: ru

Здравствуйте! Часто в повседневной практике программирования мы
используем те или иные конструкции php не задумываясь о их
производительности. А учитывая, что VDS сейчас стоят не дёшево, нужно
стараться уменьшить нагрузку наших приложений всеми доступными
средствами. Сегодня я проведу сравнительный тест разных конструкций
языка php выполняющих сходные функции. Выбрав оптимальные, по
результатам теста, конструкции вы сможете не только отложить покупку
более дорого серверного оборудования, но и просто ускорить работу ваших
сайтов, что уж точно оценят пользователи. Итак, поехали!

Тестирование производительности
-------------------------------

### "Конкатенация строк" vs "Двойные кавычки"

Данная конструкция используется в каждом приложении и очень часто,
поэтому стоит оценить различные варианты конкатенации строк:

	:::php
	<?php
	// ...
	// Двойные кавычки
	$string = "count - $i";
	// Конкатенация
	$string = 'count - ' . $i;

Тип конструкции | Время выполнения
:---------------|:----------------
Двойные кавычки | 0.505 с
Конкатенация    | 0.424 с

Конкатенация работает быстрее приблизительно на 16%.

### Обход массивов

Теперь проверим производительность различных способов перебора элементов
массива. В качестве примера будем считать сумму элементов массива,
обходя его различными способами

	:::php
	<?php
	// ...
	// Способ №1. Простой foreach без ключа
	foreach ($array as $item){
	    $summ += $item;
	}
	// Способ №2. Foreach с выборкой ключа
	foreach ($array as $key=>$item){
	    $summ += $item;
	}
	// Способ №3. Foreach с получением значения по ссылке
	foreach ($array as $key=>&$item){
	    $summ += $item;
	}
	// Способ №4. Цикл For и функция next()
	$summ = current($array);
	for ($i = 0; $i < $size; $i++){
	    $summ += next($array);
	}
	//Способ №5. While и функция each()
	while (list($key, $value) = each($array)){
	    $summ += $value;
	}
	//Способ №6. Обычный For
	for ($i=0; $i<$count; $i++){
	    $summ += $array[$i];
	}

Тип конструкции                                    | Время выполнения
:--------------------------------------------------|:----------------
Способ №1. Простой foreach без ключа               | 0.112 с
Способ №2. Foreach с выборкой ключа                | 0.131 с
Способ №3. Foreach с получением значения по ссылке | 0.144 с
Способ №4. Цикл For и функция next()               | 0.383 с
Способ №5. While и функция each()                  | 1.180 с
Способ №6. Обычный For                             | 0.120 с

Как выяснилось наиболее быстрым способом обхода массива является foreach
без выборки ключа. Также на мой взгляд данный способ является наиболее
удобным, а если совершать выборку ключа и/или значения по ссылке, то он
становится наиболее универсальным. Также неплохой результат показал
классический цикл for с перебором элементов используя числовые индексы в
естественном порядке, но очевидно данный способ нельзя использовать для
перебора ассоциативных массивов, что является огромным минусом. Самым
"прожорливым" оказался while с использованием функции each, т.к. он не
дает никаких особых преимуществ и по сути повторяет функционал foreach,
то использовать его нет смысла.

### Добавление элементов в конец массива

Тоже довольно часто используемой операцией является добавление новых
элементов в конец массива. Протестируем наиболее часто используемые
способы:

	:::php
	<?php
	// ...
	//Способ №1. 
	$array[] = $i;
	//Способ №2
	array_push($array, $i);

Тип конструкции | Время выполнения
:---------------|:----------------
Способ №1       | 0.503 с
Способ №2       | 0.998 с

Как вы видите первый способ работает в 2 раза быстрее и при этом менее
громоздок. Поэтому я рекомендую использовать именно его.

### "Оператор ветвления" vs "Тернарный оператор"

Теперь сравним производительность стандартной операции ветвления на
примере if-else и тернарного оператора:

	:::php
	<?php
	// ...
	// if-else
	if ( ($i % 2) == 0 )
	    $summ += $i;
	else
	    $summ -= $i;
	// Тернарный оператор
	$summ += (($i % 2) == 0)?$i:(-$i);

Тип конструкции    | Время выполнения
:------------------|:----------------
if-else            | 0.126 с
Тернарный оператор | 0.176 с

Тернарный оператор не на много, но всё же отстает от классического
if-else, но т.к. тернарный оператор менее громоздок, то его можно
использовать, если конечно это происходит не в цикле на миллион итераций
;)

### Проверка существования/не-равенство-null переменной

Часто бывает необходимо проверить существует ли переменная и/или равна
null. Для этого можно воспользоваться несколькими методами, например
одной из стандартных функций php (is\_null, isset, empty) или просто
сравнивать переменную с null. Протестируем каждый из этих способов:

	:::php
	<?php
	// ...
	// Сравнение с null
	if ($a != null){
	    $summ += $i;
	}
	// Эквивалентно null
	if ($a !== null){
	    $summ += $i;
	}
	// isset
	if (isset($a)){
	    $summ += $i;
	}
	// is_null
	if (!is_null($a)){
	    $summ += $i;
	}
	//empty
	if (!empty($a)){
	    $summ += $i;
	}

Тип конструкции                     | Время выполнения
:-----------------------------------|:----------------
Сравнение с null "=="               | 0.652 с
Эквивалентное сравнение с nul "===" | 0.709 с
isset                               | 0.080 с
is\_null                            | 1.021 с
empty                               | 0.105 с

Как вы видите isset оставил всех конкурентов далеко позади глотать пыль.
Рекомендую использовать именно isset, т.к. он кроме того что работает
намного быстрее всех остальных способов, ещё и не генерирует notice'ов,
так что если вы не уверены установлена ли переменная, лучше проверить её
при помощи isset и быть спокойным, т.к. никаких нотисов не будет
выводится. Также стоит отметить первый способ, т.к. он не совсем
подходит под данную категорию и он будет возвращать true, при любом
значении переменной являющемся ложным, будь-то null, не установленная
переменная или пустая строка.

Отступление: производительность и сообщения об ошибках php
----------------------------------------------------------

Интерпретатор php генерирует множество разных сообщений: ошибки,
предупреждения, уведомления и тд. При разработке эти сообщения
безусловно помогают в поиске ошибок и их устранении, но также они имеют
и негативное влияние, а именно - жуткое снижение производительности.
Проведём простой тест:

	:::php
	<?php
	// ...
	error_reporting(null);
	$timer->start();
	$a = 0;
	for ($i=0; $i<=100000; $i++){
	    $a += $i;
	    if (!is_null($b))
	        $a = 0;
	}
	echo $timer->end();

Вроде бы простой участок кода, не должен вызывать никаких осложнений. И
действительно результат выполнения данного теста показывает 0.110 с. А
теперь мы попробуем убрать первую строку отвечающую за подавление ошибок
и получим следующий результат: 1.11 c. Т.е. время выполнения увеличилось
в 10 раз! А всё из-за чего? Из-за того, что переменная $b не была
определена и соответственно php сгенерировал notice. Из этого стоит
сделать вывод - сообщения об ошибках только при разработке, но никак не
на продакшене.

Заключение
----------

На этом всё, в заключении хочу представить конфигурацию системы на
которой проводил тесты: Intel Core 2 Duo E8200 (2.6 Ггц), 2 Гб ОП,
Debian 6.0, PHP 5.3.3-7 with Suhosin-Patch, Apache 2.2.16. Возможно в
скором времени я протестирую производительность других конструкций php,
поэтому подписывайтесь на RSS-ленту, чтобы быть в теме :) Спасибо за
внимание!