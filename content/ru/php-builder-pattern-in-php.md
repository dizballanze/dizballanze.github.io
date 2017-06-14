Title: Builder (строитель)
Date: 2011-02-20 18:27
Author: Admin
Category: Другое
Tags: builder, PHP, ООП, Паттерны проектирования

![builder pattern][]

И снова рассуждение на тему порождающих шаблонов. На этот раз будем
говорить о паттерне строитель. Данный паттерн позволяет скрыть
инициализацию сложного объекта и создает простой интерфейс для
инстанциирования сложных объектов с различным внутренним состоянием.

Описание
--------

Если при проектировании вы столкнулись с тем что необходимо создавать
сложные объекты, инициализация которых состоит из нескольких этапов и
при этом вы не уверены в том что в дальнейшем инициализация данного
объекта не изменится, то стоит задуматься над использованием паттерна
строитель. Данный паттерн изолирует код отвечающий за настройку сложных
объектов и предоставляет единую точку входа для создания и получения
доступа к этим объектам.

Для реализации функций создания и настройки объектов создаётся иерархия
строителей, каждый класс данной иерархии "умеет" определённым образом
настраивать порождаемый объект и по запросу возвращает уже готовый к
работе, настроенный объект. При этом вызывающий код может не знать каким
именно образом настраивается экземпляр класса-продукта, т.к. эти
обязанности принимает на себя строитель. Кроме классов строителей также
создается, т.н. директор - класс который работает со строителем,
инициирует создание объекта-продукта и его настройки, при этом не имея
представления о процессе настройки объекта, используя только интерфейс
класса строителя. Преимущество данного шаблона заключается не только в
инкапсуляции инициализации сложного объекта, но и в выборе определённого
типа настройки объекта во время выполнения программы.

Реализация
----------

Теперь, как всегда, рассмотрим реализацию данного шаблона на нашем
любимом языке - PHP. Допустим нам нужно спроектировать иерархию классов
отвечающих за воспроизведение видео-роликов в различных форматах:

	:::php
	<?php
	class Player{
	    protected $video_codec;
	    protected $audio_codec;
	    protected $width;
	    protected $height;
	    protected $volume;
	 
	    public function setVideoCodec($codec){
	        $this->video_codec = $codec;
	    }
	 
	    public function setAudioCodec($codec){
	        $this->audio_codec = $codec;
	    }
	 
	    public function setWidth($width){
	        $this->width = $width;
	    }
	 
	    public function setHeight($height){
	        $this->height = $height;
	    }
	 
	    public function setVolume($volume){
	        $this->volume = $volume;
	    }
	 
	    public function play($some_data){
	        // Let's rock!
	    }
	}
	 
	abstract  class PlayerBuilder{
	    protected $player;
	 
	    public function createPlayer(){
	        $this->player = new Player();
	    }
	 
	    public function getPlayer(){
	        return $this->player;
	    }
	 
	    abstract function setVideoCodec();
	    abstract function setAudioCodec();
	    abstract function setWidth();
	    abstract function setHeight();
	    abstract function setVolume();
	}
	 
	class HDPlayerBuilder extends PlayerBuilder{
	    public function setVideoCodec() {
	        $this->player->setVideoCodec('some greate codec');
	    }
	 
	    public function  setAudioCodec() {
	        $this->player->setAudioCodec('some cool codec');
	    }
	 
	    public function setWidth() {
	        $this->player->setWidth(1280);
	    }
	 
	    public function setHeight() {
	        $this->player->setHeight(960);
	    }
	 
	    public function setVolume() {
	        $this->setVolume(100);
	    }
	}
	 
	class SimplePlayerBuilder extends PlayerBuilder {
	    public function setVideoCodec() {
	        $this->player->setVideoCodec('some bad codec');
	    }
	 
	    public function  setAudioCodec() {
	        $this->player->setAudioCodec('some default codec');
	    }
	 
	    public function setWidth() {
	        $this->player->setWidth(320);
	    }
	 
	    public function setHeight() {
	        $this->player->setHeight(240);
	    }
	 
	    public function setVolume() {
	        $this->setVolume(50);
	    }
	}
	 
	class Media{
	    private $_builder;
	 
	    public function  __construct(PlayerBuilder $builder) {
	        $this->_builder = $builder;
	        $this->_builder->createPlayer();
	        $this->_builder->setAudioCodec();
	        $this->_builder->setVideoCodec();
	        $this->_builder->setWidth();
	        $this->_builder->setHeight();
	        $this->_builder->setVolume();
	    }
	 
	    public function getPlayer(){
	        return $this->_builder->getPlayer();
	    }
	}

Как вы наверное уже догадались продуктом в данном случае у нас будут
объекты класса Player, строителями - объекты наследующие PlayerBuilder,
а директором - Media. Каких-то дополнительных пояснений на мой взгляд
данный код не требует, перейдем к примеру использования:

	:::php
	<?php
	// ...
	$media = new Media(new HDPlayerBuilder());
	$player = $media->getPlayer();
	$player->play('Some_Cool_Video_File.mkv');

Таким образом можно использовать вышеописанные классы. Как вы видите
здесь всё довольно просто и очевидно, создаем экземпляр директора
(Media), передаем ему нужного строителя, вызываем нужный метод и вуаля -
плеер создан :).

Спасибо всем, кто дочитал, не забывайте комментировать, т.к. ваши
комментарии = стимул написания новых статей.

  [builder pattern]: /media/2011/02/images.jpg
    "builder"
