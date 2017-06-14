Title: Abstract Factory (абстрактная фабрика)
Date: 2011-01-30 01:34
Author: Admin
Category: Другое
Tags: abstract factory, PHP, ООП, Паттерны проектирования

Рассмотрим ещё один порождающий шаблон - абстрактная фабрика. Перед
прочтением рекомендую ознакомится с шаблоном Factory Method [здесь][],
т.к. в данном топике я буду расширять рассмотренный там пример.

Описание
--------

Во время проектирования может возникнуть необходимость создавать
взаимосвязанные объекты из различных иерархии при этом решение о том
какие именно объекты создавать должно приниматься в процессе работы
программы. Например, если взять за основу пример с формами, нам может
понадобится кроме формы также создавать экземпляр класса валидатора,
который умеет проверять корректность данных в форме. Т.е. у нас есть
следующие иерархии:

	:::php
	<?php
 
	//Иерархия классов форм
	abstract class Form{
	    abstract public function generateForm();
	}
	 
	class RegForm extends Form{
	    public function generateForm() {
	        echo "Generate registration form!";
	    }
	}
	 
	class AuthForm extends Form{
	    public function generateForm() {
	        echo "Generate authentication form!";
	    }
	}
	 
	class PostForm extends Form{
	    public function generateForm() {
	        echo "Generate posting form!";
	    }
	}
	 
	//Иерархия классов валидаторов
	abstract class Validator {
	    abstract public function validate();
	}
	 
	class RegValidator extends Validator {
	    public function validate() {
	        echo 'Validate RegForm';
	    }
	}
	 
	class AuthValidator extends Validator {
	    public function validate() {
	        echo 'Validate AuthForm';
	    }
	}
	 
	class PostValidator extends Validator {
	    public function validate() {
	        echo 'Validate PostForm';
	    }
	}

У нас есть две иерархии классов и в зависимости от каких-то заранее
неизвестных параметров нам нужно уметь создавать связанные экземпляры
классов из этой иерархии. Т.е. для класса RegForm нам нужно создавать
RegValidator и тд. Для решения этой проблемы необходимо воспользоваться
шаблоном абстрактной фабрики.

Данный шаблон подразумевает наличие абстрактного класса фабрики, который
предоставляет интерфейс для создания взаимосвязанных объектов. Дочерние
классы фабрики реализуют функционал для создания экземпляров какого-то
одного набора компонентов.

Реализация
----------

Применим шаблон абстрактная фабрика к нашему примеру для создания
связанных объектов: форм и валидаторов к ним:

	:::php
	<?php
	//Иерархия фабрик
	abstract class FormFactory{
	    abstract public function getForm();
	    abstract public function getValidator();
	}
	 
	class RegFormFactory extends FormFactory{
	    public function getForm() {
	        return new RegForm();;
	    }
	 
	    public function getValidator() {
	        return new RegValidator();
	    }
	}
	 
	class AuthFormFactory extends FormFactory{
	    public function getForm() {
	        return new AuthForm();;
	    }
	 
	    public function getValidator() {
	        return new AuthValidator();
	    }
	}
	 
	class PostFormFactory extends FormFactory{
	    public function getForm() {
	        return new PostForm();;
	    }
	 
	    public function getValidator() {
	        return new PostValidator();
	    }
	}
	 
	//Иерархия классов форм
	abstract class Form{
	    abstract public function generateForm();
	}
	 
	class RegForm extends Form{
	    public function generateForm() {
	        echo "Generate registration form!";
	    }
	}
	 
	class AuthForm extends Form{
	    public function generateForm() {
	        echo "Generate authentication form!";
	    }
	}
	 
	class PostForm extends Form{
	    public function generateForm() {
	        echo "Generate posting form!";
	    }
	}
	 
	//Иерархия классов валидаторов
	abstract class Validator {
	    abstract public function validate();
	}
	 
	class RegValidator extends Validator {
	    public function validate() {
	        echo 'Validate RegForm';
	    }
	}
	 
	class AuthValidator extends Validator {
	    public function validate() {
	        echo 'Validate AuthForm';
	    }
	}
	 
	class PostValidator extends Validator {
	    public function validate() {
	        echo 'Validate PostForm';
	    }
	}

Реализовав иерархию фабрик - FormFactory мы добились нескольких важных
улучшений:

-   Гарантия того, что мы будем использовать именно нужную комбинацию
    функционально связанных классов (т.е. к форме регистрации не будет
    применяться валидатор формы авторизации).
-   Простой способ добавления новых типов компонентов.
-   Упрощенная замену классов, т.к. их инициализация вынесена в одну
    общую точку.

Но есть и явный недостаток - добавления новых компонентов в систему
требует переработки всех классов фабрик, в том числе и абстрактного.
Если вы планируете часто расширяться в сторону увеличения компонентов,
то вам стоит задуматься о другом решении.

  [здесь]: /PHP/factory-method-fabrichnyi-metod/
