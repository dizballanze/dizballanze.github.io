Title: Yii + Selenium на debian 6
Date: 2012-03-08 23:07
Author: Admin
Category: Другое
Tags: selenium, yii, магия

Для функционального тестирования в Yii используется Selenium. На debian
и ubuntu при запуске тестов выдается ошибка:

	:::text
	Result is neither "true" nor "false": 'OR Server Exception: sessionId led to start new browser session: Browser not supported

В попытках решить данную проблему были испробованы чуть меньше чем все
версии selenium и огромное количество браузеров. Однако что бы я не
делал результата это не давало. Как оказалось selenium не получает
настройки от yii (protected/tests/phpunit.xml) и по-этому не знает какой
браузер использовать. Для решения этой проблемы я установил браузер
по-умолчанию при запуске selenium'а следующим образом:

	:::bash
	DISPLAY=:0 java -jar selenium-server-standalone-2.20.0.jar -forcedBrowserMode "*googlechrome"

После этого все заработало, но очевидно только в том браузере который
указан параметром forcedBrowserMode. Мне таким образом удалось запустить
firefox и google chrome последних версий, на selenium rc 1.0.3 и
selenium sever 2.20

Если вы знаете как решить данную проблему без указания стандартного
браузера, поделитесь в комментариях, буду признателен :)

### UPDATE \#1

Возможно проблемы в текущей версии PHPUnit\_Selenium

### UPDATE \#2

Проблема решается обновление PHPUnit с [GitHub'а][].

  [GitHub'а]: https://github.com/sebastianbergmann/phpunit/
