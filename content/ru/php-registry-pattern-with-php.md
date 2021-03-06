Title: Registry (реестр)
Date: 2011-02-28 21:38
Author: Admin
Category: Другое
Tags: global variables, interfaces, json, magic methods, PHP, registry, serialize, singleton, ООП, Паттерны проектирования
Lang: ru

![registry][]

Рассмотрим паттерн проектирования - реестр. Данный паттерн является
чем-то вроде безопасной замены глобальных переменных. При помощи данного
шаблона вы сможете обмениваться данными в многоуровневом приложении.

Описание
--------

Наверное все сложные системы являются многоуровневыми, иначе мы бы
просто не смогли уследить за всеми зависимостями и связями внутри
системы. Разбивая систему на независимые уровни обменивающиеся данными
только через строго определённый интерфейс мы получаем возможность
менять реализацию отдельных уровней не опасаясь потерять
работоспособность системы. Но при этом мы получаем ряд ограничений,
главным из которых является сложность реализации обмена данными между не
смежными уровнями. Вот тут-то мы и вспоминаем о том, как хорошо было
использовать глобальные переменные и не заботится о том, что-бы данные
были доступны в определённом месте приложения. Но т.к. причины отказа от
использования глобальных переменных были более чем серьёзными нам нужно
искать другое решение проблемы.

К счастью мы не первые, кто столкнулся с подобной проблемой. Решение уже
было найдено и им является - паттерн Registry. Данный паттерн
представляет собой класс, который хранит в себе некоторые данные (часто
объекты, но не обязательно) и предоставляет к ним доступ через
статические методы или как шаблон [одиночка][]. Т.к. получить доступ к
такому классу можно из любой точки приложения, то мы получаем все
преимущества глобальных переменных без некоторых их недостатков. Теперь,
например, вы не сможете случайно затереть важные данные, т.к. это может
произойти с глобальными переменными.

Реализация
----------

Типичным примером паттерна реестр является объект хранящий параметры
системы в виде древовидной структуры. Т.к. доступ к конфигурациям
системы может потребоваться на любом уровне приложения, то мы можем
воспользоваться паттерном реестр. Обеспечив единою точку для доступа к
параметрам мы получаем дополнительные преимущества, например, мы
перестаем зависеть от способа хранения конфигураций и можем легко
перейти от хранения параметров в ini-файле к хранению в БД или в
memcache. Итак, реализуем такой класс на языке php:

	:::php
	<?php
	/**
	 * Интерфейс загрузчиков ресурсов, отвечает за загрузку ресурсов из хранилища, 
	 * должен возвращать массив параметров
	 */
	abstract class Loader{
	    abstract public function load();
	}
	 
	/**
	 * Класс загрузчик параметров из файла содержащего сериализованные данные
	 */
	class Serialize_File_Loader extends Loader{
	    protected $path = '';
	 
	    public function __construct($path) {
	        if (0 == strlen($path))
	            throw new Exception ('Должен быть указан путь к файлу с параметрами в формате сериализавонного массива php');
	        $this->path = $path;
	    }
	 
	    public function load() {
	        if (!file_exists($this->path) || !is_readable($this->path))
	            throw new Exception ('Файл не существует или его невозможно считать');
	        $array = unserialize(file_get_contents($this->path));
	        if (!$array || !is_array($array))
	            throw new Exception ('Некорректный формат файла');
	        return $array;
	    }
	}
	 
	/**
	 * Класс загрузчик параметров из файла содержащего данные в формате JSON
	 */
	class JSON_File_Loader extends Loader{
	    protected $path = '';
	 
	    public function __construct($path) {
	        if (0 == strlen($path))
	            throw new Exception ('Должен быть указан путь к файлу с параметрами в формате JSON');
	        $this->path = $path;
	    }
	 
	    public function load() {
	        if (!file_exists($this->path) || !is_readable($this->path))
	            throw new Exception ('Файл не существует или его невозможно считать');
	        $array = json_decode(file_get_contents($this->path), true);
	        if (!$array || !is_array($array))
	            throw new Exception ('Некорректный формат файла');
	        return $array;
	    }
	}
	 
	class Parameters_Registry implements Countable, Iterator{
	    /**
	     * Собственно данные
	     * @var array
	     */
	    protected $data = array();
	 
	    /**
	     * Статическая переменная - ссылается на экземпляр данного класса
	     * @var type 
	     */
	    static protected $instance = null;
	 
	    /**
	     * Метод инициализации, необходимо запускать перед началом работы
	     * @param Loader $loader - загрузчик параметров
	     */
	    public static function init(Loader $loader){
	        self::$instance = new Parameters_Registry($loader->load());
	    }
	 
	    /**
	     * Реализуем паттерн Singleton
	     * @return type 
	     */
	    public static function getInstance(){
	        if (is_null(self::$instance))
	            throw new Exception ('Реест должен быть инициализирован перед использованием!');
	        return self::$instance;
	    }
	 
	    /**
	     * Закрытый конструктор, необходим для реализации Singleton
	     * @param array $data 
	     */
	    protected function __construct(Array $data) {
	        $this->data = $data;
	    }
	 
	    /**
	     * Магические методы и реализация интерфейсов
	     */
	    public function __get($name) {
	        if (!array_key_exists($name, $this->data)){
	            trigger_error('Неизвестный параметр: ' . $name, E_USER_NOTICE);
	            return null;
	        }
	 
	        if (!is_array($this->data[$name]))
	            return $this->data[$name];
	        // Если массив, то создаём ещё один экземпляр класса параметров, инициализируем
	        // его данными этого массива, ставим на его место в массиве данных
	        // и возвращаем.
	        return $this->data[$name] = new Parameters_Registry($this->data[$name]); // %)
	    }
	 
	    public function __set($name, $value) {
	        $this->data['name'] = $value;
	    }
	 
	    public function count() {
	        return count($this->data);
	    }
	 
	    public function __isset($name) {
	        return isset ($this->data[$name]);
	    }
	 
	    public function __unset($name) {
	        if (array_key_exists($name, $this->data))
	            unset ($this->data[$name]);
	    }
	 
	    public function rewind() {
	        reset($this->data);
	    }
	 
	    public function current() {
	        $key = key($this->data);
	        return $this->__get($key);
	    }
	 
	    public function key() {
	        return key($this->data);
	    }
	 
	    public function next(){
	        next($this->data);
	        $key = key($this->data);
	        return $this->__get($key);
	    }
	 
	    public function valid() {
	        $key = key($this->data);
	        return ((false !== $key) && (null !== $key));
	    }
	}

Вот собственно полная иерархия классов необходимых для того, что-бы раз
и на всегда решить ваши проблемы с доступом к конфигурациям ;). А если
серьезно, то у нас есть иерархия классов наследующих Loader, они
отвечают за загрузку данных из внешних источников и должны возвращать
массив. Также у нас есть класс Parameters\_Registry, который отвечает за
предоставление глобального доступа к параметрам. На первый взгляд он
является реализацией шаблона Одиночка, но это не совсем так, для
реализации "цепочек" запросов к иерархии я создаю ещё экземпляры данного
класса, но только для внутреннего использования. В глобальной области
видимости осуществляется доступ только к одному объекту, который
создается при вызове статического метода init. Я добавил в этот класс
несколько полезных функций:

-   Интерфейс Iterator - позволяет перебирать объект, как массив при
    помощи foreach и функций для работы с массивами
-   Интерфейс Countable - позволяет вычислять количество параметров при
    помощи функции count
-   Chaining - для доступа к определённым элементам иерархии, как к
    свойствам объекта

Я уверен, что Вы без проблем придумаете новый, нужный вам функционал.
Например вы можете добавить другие типы Loader'ов или расширите
функционал реестра.

Теперь давайте протестируем полученные классы и разберемся с тем как же
можно их использовать. Генерируем тесты:

	:::php
	<?php
	// Готовим данные для тестирования
	$array = array(
	    'db'=>array(
	        'db_name'=>'test_db',
	        'db_host'=>'localhost',
	        'db_port'=>'3301',
	        'db_type'=>'MySQL',
	        'db_pass'=>'ololo'
	    ),
	    'test'=>array(
	        'test2'=>array(
	            'test3'=>array(
	                'last_one'=>'Фааааак йеееех ;['
	            )
	        )
	    )
	);
	file_put_contents('test.ser', serialize($array));
	file_put_contents('test.json', json_encode($array));

Первый тест:

	:::php
	<?php
	// ...
	Parameters_Registry::init(new JSON_File_Loader('test.json'));
	$registry = Parameters_Registry::getInstance();
	echo count($registry->db) . "\n";
	foreach ($registry->db as $key=>$value){
	    echo $key . ':' . $value . "\n";
	}

Здесь я демонстрирую Countable и Iterator. В результате выполнения
предыдущего теста получим следующее:

    :::text
    5
	db_name:test_db
	db_host:localhost
	db_port:3301
	db_type:MySQL
	db_pass:ololo

Второй тест:

	:::php
	Parameters_Registry::init(new Serialize_File_Loader('test.ser'));
	$registry = Parameters_Registry::getInstance();
	echo $registry->test->test2->test3->last_one;

Здесь вы можете увидеть, как работает chaining. Результат:
	
	:::text
    Фааааак йеееех ;[

Заключение
----------

В заключении подведем итог всему вышеизложенному. Паттерн Registry
позволяет нам получать доступ к необходим данным на различных уровнях
приложения, предоставляя единую точку доступа для всех уровней. Таким
образом мы используем более корректный вариант глобальных переменных,
который НЕ будет случайно перезаписан, НЕ засоряет глобальную область
видимости, НЕ будет иметь риск слишком поздней инициализации и тд. Но
т.к. этот паттерн все таки имеет глобальную точку доступа, он добавляет
некоторую степень связанности, поэтому его следует использовать только
тогда, когда без него не обойтись. В общем если вы не будете им
злоупотреблять, то он сделает ваше приложение более прозрачным и более
простым в расширении за счёт отсутствия необходимости в постоянной
передачи глобальных параметров от объекта к объекту. Спасибо всем, кто
дочитал, подписывайтесь на RSS, оставляйте свои комментарии!

  [registry]: /media/2011/02/Windows-7-Registry-Tricks-150x150.jpg
    "registry"
  [одиночка]: /PHP/singleton-odinochka/
