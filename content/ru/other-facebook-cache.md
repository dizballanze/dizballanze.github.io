Title: Проблема с кэшем facebook и url
Date: 2011-06-03 10:55
Author: Admin
Category: Другое
Tags: cache, facebook, url
Lang: ru

![facebook][]

Здравствуйте! Недавно столкнулся с проблемой при использовании кнопки
like от facebook. Проблема заключалась в том, что в open graph теге был
указан некорректный url. Заметив данную оплошность я сразу её устранил,
но это не повлекло за собой нужного эффекта. Как оказалось, дело в том
что facebook кэширует данные о страницах, которые были залайканы. В этом
нет ничего удивительного, если учесть под какими нагрузками он работает.
Для того, чтобы изменения вступили в силу, нужно подождать некоторое
время (где-то прочитал, что 24-32 часа).

Как оказалось, есть способ ускорить этот процесс. У facebook есть
отличный инструмент, который анализирует сайт и позволяет производить
отладку open graph тегов, также он дает полезные советы по оптимизации
работы сайта с facebook. Но в контексте нашей проблемы интерес
составляет тот факт, что использование данного инструмента сбрасывает
кэш для анализируемой страницы. Если вы столкнулись с такой же
проблемой, то [Url Linker][] вам поможет.

  [facebook]: /media/2011/06/n20531316728_2183540_7053-300x99.jpg
    "facebook"
  [Url Linker]: http://developers.facebook.com/tools/lint/
