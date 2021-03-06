Title: Factory Method (фабричный метод)
Date: 2011-01-19 18:39
Author: Admin
Category: Другое
Tags: Factory Method, PHP, ООП, Паттерны проектирования
Lang: ru

Данный топик продолжает тему шаблонов проектирования для генерации
объектов. Рассмотрим паттерн Factory Method или на великом и могучем (на
русском, а не php :)) - фабричный метод.

Описание
--------

Часто при проектировании классов возникает необходимость создавать
экземпляры одних классов внутри других. При этом могут возникнуть
требования создавать экземпляры не одного, а нескольких классов одной
иерархии. Это вполне логично и сразу же напрашивается одно решение -
использовать условия или switch к параметрам передаваемым в метод
порождающего класса и в зависимости от параметра создавать нужный
экземпляр иерархии. Если мы знаем что в порождаемой иерархии классов
всего несколько подклассов и расширение их не предвидится, то такое
решение вполне приемлемо, но часто бывает так что иерархии растут и
очень быстро и вместе с ними растет и условная конструкция. Как мы видим
сразу появляется ряд недостатков:

-   Копипаст. Может возникнуть необходимость выполнять различные
    действия в зависимости от типа порождаемого класса, что приводит к
    копированию условной конструкции в различных методах порождающего
    класса.
-   Поддержка. С ростом количества кода неизбежно усложняется его
    поддержка что приводит к усложнению нахождения ошибок. Также этот
    недостаток будет особенно сильно проявляться при совместной
    разработке, когда кто-нибудь добавит новый класс в порождающую
    иерархию изменит соответственным образом класс, который генерирует
    объекты и затрет недавно сделанные изменения своего коллеги, который
    тоже добавил новый case в N-методов класса, за что получит в лучшем
    случае гневное письмо, а в худшем черепно-мозговую травму :)

Рассмотрим упрощенный пример такого кода:

    :::php
    <?php
    define('RegForm', 1);
    define('AuthForm', 2);
    define('PostForm', 3);
     
    //Менеджер форм
    class FormManager{
        protected $type;
     
        public function __construct($type=1) {
            $this->type = $type;
        }
     
        public function getForm(){
            switch ($this->type){
                case RegForm:
                    return new RegForm();
                    break;
                case AuthForm:
                    return new AuthForm();
                    break;
                case PostForm:
                    return new PostForm();
                    break;
            }
        }
    }
     
    // Иерархия классов форм
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

В данном упрощенном примере рассматривается реализация менеджера форм,
который в зависимости от переданного в конструктор параметра создает
нужный класс формы. Как мы видим использование switch-конструкции здесь
не очень удобно, т.к. требует модификации кода класса при добавлении
нового класса в иерархию форм. А представьте себе ситуацию, что менеджер
форм должен иметь ещё какой-либо функционал, который также зависит от
типа формы, в результате мы получим большое количество методов с
одинаковыми switch-конструкциями. Вообщем на лицо проблема и решить её
можно воспользовавшись шаблоном Factory Method.

Суть данного шаблона заключается в создании иерархии порождающих
классов, каждый дочерний класс иерархии "знает" какой именно класс из
порождаемого дерева классов ему нужно инстанциировать. Т.е. мы создаем
параллельную иерархию порождающих классов, которая в точности
соответствует иерархии порождаемых классов.

Реализация
----------

Рассмотрим предыдущий пример улучшенный путём использования шаблона
Factory Method:

    :::php
    <?php
    //Иерархия генерирующих классов
    abstract class FormManager{
        abstract public function getForm();
    }
     
    class RegFormManager extends FormManager{
        public function getForm() {
            return new RegForm();
        }
    }
     
    class AuthFormManager extends FormManager{
        public function getForm() {
            return new AuthForm();
        }
    }
     
    class PostFormManager extends FormManager{
        public function getForm() {
            return new PostForm();
        }
    }
     
    //Иерархия генерируемых классов
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

Здесь мы видим, что создается ещё одна иерархия классов, дочерних
FormManager. Каждый класс в иерархии FormManager создает экземпляр
определённого класса иерархии Form. Воспользовавшись рассматриваемым
шаблоном мы значительно улучшили ситуацию. Теперь для добавления новой
формы не нужно редактировать код классов, всё сводится к добавлению
нового класса в иерархию FormManager. Это дает нам ряд преимуществ,
например более удобную поддержку кода и отсутствие жутких условных или
switch конструкций. Но мы получили и недостаток - растущую иерархию
классов, так что если у вас нет серьёзных причин в использовании данного
шаблона, то следует подумать о каком-либо другом решении.
