Title: Наследование свойств моделей в Mongoose
Date: 2013-01-02 02:41
Author: Admin
Category: Node.js
Tags: mongoose, mongodb, node.js, sugar.js

Всех с прошедшим Новым Годом! Сегодня я покажу как наследовать свойства
моделей в [ODM Mongoose](http://mongoosejs.com/ "Mongoose ODM"). Для тех, кто не знает mongoose - это 
ODM (object document mapper) для node.js и [MongoDB](http://www.mongodb.org/ "MongoDB"). 

Применение
----------
Часто бывает необходимо в рамках одной коллекции объектов выделить несколько
типов с некоторыми различиями в наборе свойств. Т.к. MongoDB реализует schema-less дизайн, 
мы не ограничены базой данных и не обязаны следовать какому-то строгому набору
полей в наших коллекциях. Однако, удобнее использовать ODM, которые реализовывают
дополнительные плюшки, такие как валидация, фильтрация, методы модели и т.д.
Соответственно описание данных на уровне исходного кода модели все же остаётся.
Для того, чтобы решить проблему с типами объектов в рамках одной коллекции можно
наследовать базовые свойства и дополнять их специфическими для каждого типа объектов.

Рассмотрим простой пример. У нас есть два типа пользователей: юридическое лицо и физическое
лицо. Каждый тип имеет общие и специфические поля. Чтобы выделить общие поля создадим объект
с набором полей, которые встречаются в каждом из типов:

    :::javascript
	var BaseUser = {
		inn: {type: String, 
			validate: inn_validator,
			required: true},
		email: {type: String, required: true, unique: true,
			validate: email_validator},
		phone: {type: String, validate: phone_validator,
			required: true},
		username: {type: String, unique: true,
			required: true, validate: username_validator},
		password: {type: String, required: true, 
			validate: password_validator}
	};

Далее для каждого из типов пользователей создаём объект со специфическими полями:

	:::javascript
	// Физическое лицо
	var IndividualPerson = {
		first_name: {type: String, required: true,
			validate: first_name_validator},
		last_name: {type: String, required: true,
			valdiate: last_name_validator},
		patronymic: {type: String, 
			validate: patronymic_validator},
		type: {type: String, default: 'individual'}
	};

	// Юридическое лицо
	var LegalPerson = {
		full_name: {type: String, validate: full_name_validator, 
			required: true},
		short_name: {type: String, required: true, 
			validate: short_name_validator},
		type: {type: String, default: 'legal'}
	};

Также мы добавили поле `type` для дифференциации записей, т.к. они будут храниться в одной коллекции.
Далее необходимо просто при создании схемы модели выполнять слияние (merge) значений из `BaseUser` и
соответствующего объекта типа:

	:::javascript
	IndividualUserSchema = new Schema(Object.extended(BaseUser).merge(IndividualPerson));
	LegalUserSchema = new Schema(Object.extended(BaseUser).merge(LegalPerson));

Здесь я использую [sugar.js](http://sugarjs.com/ "Sugar.js"), но при необходимости это можно реализовать
и вручную.

Затем модели необходимо создавать таким образом, чтобы они использовали одну и ту же коллекцию в базе данных:

	:::javascript
	exports.LegalUser = function(db) {
		return db.model('LegalUser', LegalUserSchema, 'users');
	};

	exports.IndividualUser = function(db) {
		return db.model('IndividualUser', IndividualUserSchema, 'users');
	};

Заключение
----------
В итоге мы получили две модели со своими наборами полей/валидаторов и при этом остались
преимущества использования одной коллекции - поиск записей по одной коллекции, уникальные
значения `username` и `email` через индексы и т.д.
При желании можно реализовать что-то вроде фабрики, чтобы при поиске в зависимости от значения
в поле `type` создавался объект соответствующей модели.