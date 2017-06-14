Title: Prototype (прототип)
Date: 2011-02-19 23:47
Author: Admin
Category: Другое
Tags: ООП, Паттерны проектирования
Lang: ru

Следующий порождающий объекты шаблон, который мы рассмотрим - прототип.
Данный шаблон является более гибкой версией шаблона Abstract Factory.

Описание
--------

Часто приходится отказываться от затеи использовать шаблон [абстрактная
фабрика][] из-за необходимости поддерживать дополнительные иерархии
классов. С этой проблемой нам может помочь шаблон prototype, который
основан на использовании средства clone языка php для создания копий
объектов.

![prototype pattern][]

Данный шаблон подразумевает наличие класса,
объекты которого хранят внутри себя, как свойство некоторые эталонные
экземпляры порождаемых классов. При этом условием начала работы с
объектом-прототипом есть инициализация его этими эталонными объектами,
как правило они передаются в конструктор, но могут быть установлены и
при помощи других методов прототипа. После инициализации прототипа к
нему можно обращаться непосредственно для генерации объектов, что
приведет к созданию полностью идентичной копии эталонного объекта и
возврату его вызывающему коду. Так как мы используем готовые объекты для
инициализации прототипа, то нам больше не нужно создавать параллельные
иерархии классов. Но это не единственно преимущество данного шаблона.
Если копнуть глубже, то можно найти много новых возможностей, например
из-за того что мы получаем точную копию эталонного объекта, а не новый
объект, как в шаблоне абстрактная фабрика, мы получаем дополнительные
возможности в виде настройки эталонного объекта (изменение значения
свойств). Также гибкость достигается и в не обязательном соответствии
комбинаций взаимосвязанных классов, так как это было в шаблоне
абстрактная фабрика.

Реализация
----------

Давайте разберем простой пример реализации данного шаблона. Представим,
что нам нужно спроектировать иерархию классов которая буде отвечать за
стиль отображения страницы документа. Ограничимся настройкой стилей
параграфов, заголовков и списков. Для каждого из элементов у нас будет
своя иерархия классов которая позволит выводить данный элемент скажем на
принтер и браузер. Теперь собственно пример такой иерархии (без
реализации, т.к. нас интересует только логические понятия, а не сам
функционал):

	:::php
	<?php
	 
	abstract class Paragraph{
	    abstract public function format($data);
	}
	 
	abstract class Header{
	    abstract public function header_big($data);
	    abstract public function header_small($data);
	}
	 
	abstract class Lists{
	    abstract public function numeric($data);
	    abstract public function alpha($data);
	}
	 
	class PrintedParagraph extends Paragraph{
	    public function format($data){
	        // Some operations
	    }
	}
	 
	class PrintedHeader extends Header{
	    public function header_big($data){
	        // Some operations
	    }
	    public function header_small($data){
	        // Some operations
	    }
	}
	 
	class PrintedLists extends Lists {
	    public function numeric($data){
	        // Some operations
	    }
	 
	    public function alpha($data) {
	        // Some operations
	    }
	}
	 
	class BrowsedParagraph extends Paragraph{
	    public function format($data){
	        // Some operations
	    }
	}
	 
	class BrowsedHeader extends Header{
	    public function header_big($data){
	        // Some operations
	    }
	    public function header_small($data){
	        // Some operations
	    }
	}
	 
	class BrowsedLists extends Lists {
	    public function numeric($data){
	        // Some operations
	    }
	 
	    public function alpha($data) {
	        // Some operations
	    }
	}
	 
	class DocumentPrototype {
	    protected $_paragraph;
	    protected $_header;
	    protected $_list;
	 
	    public function __construct(Paragraph $paragraph, Header $header, Lists $list) {
	        $this->_paragraph = $paragraph;
	        $this->_header = $header;
	        $this->_list = $list;
	    }
	 
	    public function getParagraph(){
	        return clone $this->_paragraph;
	    }
	 
	    public function getHeader(){
	        return clone $this->_header;
	    }
	 
	    public function getList(){
	        return clone $this->_list;
	    }
	}

Итак, что мы тут видим. У нас имеется 3 иерархии классов, которые
позволяют форматировать различные элементы документа и нам необходимо
создавать экземпляры этих классов в процессе работы программы,
экземпляры каких именно классов нам нужно создавать заранее не известно.
По-этому мы реализовываем ещё один класс - DocumentPrototype, который
как вы уже наверное догадались, представляет собой паттерн прототип. Как
вы видите данный класс принимает в конструкторе эталонные экземпляры
классов-элементов документа и потом умеет создавать их копии при помощи
соответствующих методов. Рассмотрим пример использования данного класса:

	:::php
	<?php
	// ...
	$document = new DocumentPrototype(new BrowsedParagraph(), new BrowsedHeader(), new BrowsedLists());
	$list = $document->getList();
	$list->numeric(array('first','second', 'third'));
	$header = $document->getHeader();
	$header->header_big('Test');

Мы получаем возможность создавать объекты без поддержки дополнительных
иерархий классов. Теперь давайте представим, что нам нужно создать
документ у которого бы параграфы выводились так, как если бы они
выводились на печать, а заголовки и списки, так, как на web-странице:

	:::php
	<?php
	// ...
	$document = new DocumentPrototype(new PrintedParagraph(), new BrowsedHeader(), new BrowsedLists());

Всё довольно просто, мы всего лишь заменили один аргумент конструктора
на другой и получили такой отличный результат. К примеру каждый из этих
классов может принимать массив параметров в котором указываются какие-то
настройки стиля отображения элементов, теперь нам для того что-бы скажем
увеличить размер шрифта заголовка нужно всего лишь изменить эталонный
объект следующим образом:

	:::php
	<?php
	// ...
	$header = new BrowsedHeader(array('font-size'=>'200%'));
	$document = new DocumentPrototype(new PrintedParagraph(), $header, new BrowsedLists());

Вот таким простым способом мы увеличили размер шрифта всех заголовков
документа.

В подведении итогов перечислим преимущества паттерна Prototype:

-   Нет необходимости сопровождать дополнительные иерархии классов
-   Гибкость настройки эталонных объектов
-   Гибкость композиции
-   Простое масштабирование порождаемой иерархии
-   Гибкость во времени выполнения программы

Спасибо за внимание, до встречи в мире ООП ;)

*Comments - welcome!*

  [абстрактная фабрика]: /PHP/abstract-factory-abstraktnaia-fabrika/
  [prototype pattern]: /media/2011/02/clone-wars-9.jpg
    "prototype pattern"
