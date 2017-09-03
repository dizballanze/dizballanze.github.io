Title: Оптимизация производительности Django проектов (часть 3)
Slug: django-project-optimization-part-3
Date: 2017-08-03 13:53
Category: python
Tags: python, django
Lang: ru


Остальные статьи цикла:

-  [Часть 1. Профилирование и настройки Django](/ru/django-project-optimization-part-1/)
-  [Часть 2. Работа с базой данных](/ru/django-project-optimization-part-2/)
-  Часть 3. Кэширование

В этой части серии мы рассмотрим важнейший подход к обеспечению высокой производительности - кэширование. Суть кэширования
в том, чтобы размещать часто используемые данные в быстром хранилище для ускорения доступа к ним. Важно понять, что
быстрое хранилище (например, оперативная память) часто имеет очень ограниченный объем и его нужно использовать для
хранения только тех данных, которые с большой вероятностью будут запрошены.

## Кэш фреймворк Django

Django предоставляет ряд средств для кэширования из коробки. Хранилище кэша настраивается при помощи словаря `CACHES`
в `settings.py`:

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "my_cache_table",
    }
}
```

Django предоставляет несколько встроенных бекендов для кэша, рассмотрим некоторые из них:

- `DummyCache` - ничего не кэширует, используется при разработке/тестировании, если нужно временно отключить кэширование,
- `DatabaseCache` - хранит кэш в БД, не самый быстрый вариант, но может быть полезен для хранения результатов долгих
вычислений или сложных SQL запросов,
- `MemcachedCache` - использует [Memcached](http://memcached.org/) в качестве хранилища, для использования этого бекенда
вам понадобится поднять сервер(ы) Memcached.

Для использования в продакшене лучше всего подходит `MemcachedCache` и в некоторых случаях может быть полезен `DatabaseCache`.
Также Django позволяет использовать сторонние бекенды, например, удачным вариантом может быть использование Redis в
качестве хранилища для кэша. Redis [предоставляет больше возможностей](http://antirez.com/news/94) чем Memcached и вы
скорее всего и так уже используете его в вашем проекте. Вы можете установить пакет `django-redis`
и [настроить](http://niwinz.github.io/django-redis/latest/#_configure_as_cache_backend) его как бекенд для вашего кэша.


### Кэширование всего сайта

Если на вашем сайте нет динамического контента, который часто меняется, то вы можете решить проблему кэширования
просто - включив кэширование всего сайта. Для этого нужно добавить несколько настроек в `settings.py`:

```python
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    
    # place all other middlewares here

    'django.middleware.cache.FetchFromCacheMiddleware',
]

# Key in `CACHES` dict
CACHE_MIDDLEWARE_ALIAS = 'default'

# Additional prefix for cache keys
CACHE_MIDDLEWARE_KEY_PREFIX = ''

# Cache key TTL in seconds
CACHE_MIDDLEWARE_SECONDS = 600
```

После добавления показанных выше middleware первым и последним в списке, все GET и HEAD запросы будут кэшироваться на
указанное в параметре `CACHE_MIDDLEWARE_SECONDS` время.

При необходимости вы даже можете програмно сбрасывать кэш:

```python
from django.core.cache import caches
cache = caches['default']  # `default` is a key from CACHES dict in settings.py
ache.clear()
```

Или можно сбросить кэш непосредственно в используемом хранилище. Например, для Redis:

```
$ redis-cli -n 1 FLUSHDB # 1 is a DB number specified in settings.py
```

### Кэширование view

Если в вашем случае не целесообразно кэшировать весь сайт, то вы можете включить кэширование только определенных view, которые
создают наибольшую нагрузку. Для этого Django предоставляет декоратор `cache_page`:

```python
from django.views.decorators.cache import cache_page


@cache_page(600, cache='default', key_prefix='')
def author_page_view(request, username):
    author = get_object_or_404(Author, username=username)
    show_articles_link = author.articles.exists()
    return render(
        request, 'blog/author.html',
        context=dict(author=author, show_articles_link=show_articles_link))
```

`cache_page` принимает следующие параметры:

-  первый обязательный аргумент задает TTL кэша в секундах,
-  `cache` - ключ в словаре `CACHES`,
-  `key_prefix` - префикс для ключей кэша.

Также этот декоратор можно применить в `urls.py`, что удобно для Class-Based Views:

```python
urlpatterns = [
    url(r'^$', cache_page(600)(ArticlesListView.as_view()), name='articles_list'),
    ...
]
```

Если часть контента сайта меняется в зависимости, например, от того какой пользователь аутентифицирован, то такой подход
не подойдет. Для решения этой проблемы можно воспользоваться одним из вариантов описанных ниже.

### Кэширование части шаблона

В предыдущей части этой серии статей было описано, что QuerySet объекты ленивые и SQL запросы не выполняются без
крайней необходимости. Мы можем воспользоваться этим и закэшировать фрагменты шаблона, что позволит избежать SQL запросов
на время жизни кэша. Для этого нужно воспользоваться тегом шаблона `cache`:

```html
{% load cache %}

<h1>Articles list</h1>

<p>Authors count: {{ authors_count }}</p>

<h2>Top authors</h2>

{% cache 500 top_author %}
<ul>
    {% for author in top_authors %}
    <li>{{ author.username }} ({{ author.articles_count }})</li>
    {% endfor %}
</ul>
{% endcache %}

{% cache 500 articles_list %}
{% for article in articles %}
<article>
    <h2>{{ article.title }}</h2>
    <time>{{ article.created_at }}</time>
    <p>Author: <a href="{% url 'author_page' username=article.author.username %}">{{ article.author.username }}</a></p>
    <p>Tags:
    {% for tag in article.tags.all %}
        {{ tag }}{% if not forloop.last %}, {% endif %}
    {% endfor %}
</article>
{% endfor %}
{% endcache %}
```

Результат добавления тегов `cache` в шаблон (до и после соответственно):

![django-templates-caching-results](/media/2017/8/templates-caching.png)

`cache` принимает следующие аргументы:

-  первый обязательный аргумент означает TTL кэша в секундах,
-  обязательное название фрагмента,
-  не обязательные дополнительные переменные, которые идентифицируют фрагмент по динамическим данным,
-  ключевой параметр `using='default'`, должен соответствовать ключу словаря `CACHES` в `settings.py`.

Например, если нужно, чтобы для каждого пользователя фрагмент кэшировался отдельно, то нужно передать в тег `cache`
переменную которая идентифицирует пользователя:

```html
{% cache 500 personal_articles_list request.user.username %}
    <!-- ... -->
{% %}
```

При необходимости можно передавать несколько таких переменных для создания ключей на основе комбинации их значений.

### Низкоуровневое кэширование

Django предоставляет доступ к низкоуровневому API кэш фреймворка. Вы можете использовать его для
сохранения/извлечения/удаления данных по определенному ключу в кэше. Рассмотрим небольшой пример:

```python
from django.core.cache import cache

class ArticlesListView(ListView):

    ...

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        authors_count = cache.get('authors_count')
        if authors_count is None:
            authors_count = Author.objects.count()
            cache.set('authors_count', authors_count)
        context['authors_count'] = authors_count
        ...
        return context
```

В этом фрагменте кода мы проверяем, есть ли в кэше количество авторов, которое должно быть по ключу `authors_count`.
Если есть (`cache.get` вернул не `None`), то используем значение из кэша. Иначе запрашиваем значение из БД и сохраняем
в кэш. Таким образом в течении времени жизни ключа в кэше мы больше не будем обращаться к БД.

Кроме результатов запросов к БД, также есть смысл кэшировать результаты сложных вычислений или обращения к внешним сервисам.
Важно при этом учитывать, что данные могут изменится и в кэше будет устаревшая информация. Для того, чтобы минимизировать
вероятность использования устаревших данных из кэша нужно:

-  настроить адекватное TTL для кэша, которое бы соответствовало частоте изменения кэшируемых данных,
-  реализовать инвалидацию кэша.

Инвалидация кеша должна происходить по событию изменения данных. Рассмотрим, как можно реализовать инвалидацию для примера
с количеством авторов:

```python
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache


def clear_authors_count_cache():
    cache.delete('authors_count')


@receiver(post_delete, sender=Author)
def author_post_delete_handler(sender, **kwargs):
    clear_authors_count_cache()


@receiver(post_save, sender=Author)
def author_post_save_handler(sender, **kwargs):
    if kwargs['created']:
        clear_authors_count_cache()
```

Были добавлены 2 обработчика сигналов: создание и удаление автора. Теперь при изменении количества авторов
значение в кэше по ключу `authors_count` будет сбрасываться и в view будет запрашиваться новое количество авторов из БД.

## cached_property

Кроме кэш фреймворка Django также предоставляет возможность кэшировать обращение к функции прямо в памяти процесса.
Такой вид кэша возможен только для методов не принимающих никаких параметров кроме `self`. Такой кэш будет жить до тех
пор пока существует соответствующий объект.

`cached_property` это декоратор входящий в Django. Результат применения его к методу, кроме кэширования, метод становится
свойством и вызывается неявно без необходимости указания круглых скобок. Рассмотрим пример:

```python
class Author(models.Model):

    username = models.CharField(max_length=64, db_index=True)
    email = models.EmailField()
    bio = models.TextField()

    @cached_property
    def articles_count(self):
        return self.articles.count()
```

Проверим как работает свойство `article_count` с включенным логированием SQL:

```
>>> from blog.models import Author
>>> author = Author.objects.first()
(0.002) SELECT "blog_author"."id", "blog_author"."username", "blog_author"."email", "blog_author"."bio" FROM "blog_author" ORDER BY "blog_author"."id" ASC LIMIT 1; args=()
>>> author.articles_count
(0.001) SELECT COUNT(*) AS "__count" FROM "blog_article" WHERE "blog_article"."author_id" = 142601; args=(142601,)
28
>>> author.articles_count
28
```

Как вы видите, повторное обращение к свойству `article_count` не вызывает SQL запрос. Но если мы создадим еще один
экземпляр автора, то в нем это свойство не будет закэшированно, до того как мы впервые к нему обратимся, т.к. кэш в
данном случае привязан к экземпляру класса `Author`.

## Cacheops

[django-cacheops](https://github.com/Suor/django-cacheops) это сторонний пакет, который позволяет очень быстро внедрить
кэширование запросов к БД практически не меняя код проекта. Большую часть случаев можно решить просто задав ряд
настроек этого пакета в `settings.py`.

Рассмотрим на примере простой вариант использования этого пакета. В качестве тестового проекта будем использовать 
[пример](https://github.com/dizballanze/django-optimization-guide-2-sample) из прошлой части  серии.

Cacheops использует Redis в качестве хранилища кэша, в `settings.py` нужно указать параметры подключения к серверу Redis.

```python
CACHEOPS_REDIS = "redis://localhost:6379/1"

INSTALLED_APPS = [
    ...
    'cacheops',
]

CACHEOPS = {
    'blog.*': {'ops': 'all', 'timeout': 60*15},
    '*.*': {'timeout': 60*60},
}
```

Вот так просто мы добавили кэширование всех запросов к моделям из приложения `blog` на 15 минут. При этом cacheops
автоматически настраивает инвалидацию кэша не только по времени, но и по событиям обновления данных, при помощи сигналов
соответствующих моделей.

При необходимости можно настроить кэширование не только всех моделей приложения но и каждую модель отдельно и для разных
запросов. Несколько примеров:

```python
CACHEOPS = {
    'blog.author': {'ops': 'all', 'timeout': 60 * 60},  # cache all queries to `Author` model for an hour
    'blog.article': {'ops': 'fetch', 'timeout': 60 * 10},  # cache `Article` fetch queries for 10 minutes
    'blog.article': {'ops': 'get', 'timeout': 60 * 15},  # cache `Article` get queries for 15 minutes
    'blog.article': {'ops': 'count', 'timeout': 60 * 60 * 3},  # cache `Article` fetch queries for 3 hours
    '*.*': {'timeout': 60 * 60},
}
```

Кроме этого cacheops имеет ряд других функций, некоторые из них:

-  ручное кэширование `Article.objects.filter(tag=2).cache()`,
-  кэширование результатов выполнения функций с привязкой к модели и автоматической инвалидацией,
-  кэширование view с привязкой к модели и автоматической инвалидацией,
-  кэширование фрагментов шаблона и многое другое.

Рекомендую ознакомится с [README cacheops](https://github.com/Suor/django-cacheops/blob/master/README.rst) чтобы узнать
подробности.

## HTTP кэширование

Если ваш проект использует HTTP, то кроме серверного кэширования вы также можете использовать встроенные в HTTP протокол
механизмы кэширования. Они позволяют настроить кэширование результатов безопасных запросов (GET и HEAD) на клиенте
(например, браузере) и на промежуточных прокси-серверах.

Управление кэшированием осуществляется при помощи HTTP заголовков. Установку этих заголовков можно настроить в приложении
или, например, на web-сервере (Nginx, Apache, etc).

Django предоставляет middleware и несколько удобных декораторов для управления HTTP кэшем.

### Vary

Заголовок [`Vary`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Vary) позволяет задать список названий
заголовков, значения в которых будут учитываться при создании ключа кэша. Django предоставляет view декоратор
[`vary_on_headers`](https://docs.djangoproject.com/en/1.11/topics/cache/#using-vary-headers) для управления этим заголовком.

```python
from django.views.decorators.vary import vary_on_headers


@vary_on_headers('User-Agent')
def author_page_view(request, username):
    ...
```

В данном случае, для разных значений заголовка `User-Agent` будут разные ключи кэша.

### Cache-Control

Заголовок [`Cache-Control`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control) позволяет задавать
различные параметры управляющие механизмом кэширования. Для задания этого заголовка можно использовать встроенный 
в Django view декортатор
[`cache_control`](https://docs.djangoproject.com/en/1.11/topics/cache/#controlling-cache-using-other-headers).

```python
from django.views.decorators.cache import cache_control


@cache_control(private=True, max_age=3600)
def author_page_view(request, username):
    ...
```

Рассмотрим некоторые директивы заголовка `Cache-Control`:

-  `public`, `private` - разрешает или запрещает кэширование в публичном кэше (прокси серверах и тд). Это важные директивы,
которые позволяют обезопасить приватный контент, который должен быть доступен только определенным пользователям.
-  `no-cache` - отключает кэширование, что заставляет клиент делать запрос к серверу.
-  `max-age` - время в секундах, после которого считается, что контент устарел и его нужно запросить заново.

### Last-Modified & Etag

HTTP протокол предоставляет и более сложный механизм кэширования, который позволяет уточнять у сервера актуальна ли
кэшированная версия контента при помощи условных запросов. Для работы этого механизма сервер должен отдавать следующие
заголовки (один из них или оба):

-  `Last-Modified` - дата и время последнего изменения ресурса.
-  `Etag` - идентификатор версии ресурса (уникальный хэш или номер версии).

После этого при повторном обращении к ресурсу клиент должен использовать заголовки `If-Modified-Since` и `If-None-Match`
соответственно. В таком случае, если ресурс не изменился (исходя из значений Etag и/или Last-Modified), то сервер
вернет статус 304 без тела ответа. Это позволяет выполнять повторную загрузку ресурса только в том случае, если он изменился
и тем самым съекономить время и ресурсы сервера.

Кроме кэширования, описанные выше заголовки применяются для проверки предусловий в запросах изменяющих ресурс (POST, PUT и тд).
Но обсуждение этого вопроса выходит за рамки данной статьи.

Django предоставляет несколько способов задания заголовков `Etag` и `Last-Modified`. Самый простой способ - использование
`ConditionalGetMiddleware`. Этот middleware добавляет заголовок `Etag`, на основе ответа view, ко всем
GET запросам приложения. Также он проверяет заголовки запроса и возвращает 304, если ресурс не изменился.

Этот подход имеет ряд недостатков:

-  middleware применяется сразу ко всем view проекта, что не всегда нужно,
-  для проверки актуальности ресурса необходимо сгенерировать полный ответ view,
-  работает только для GET запросов.

Для тонкой настройки нужно применять декоратор `condition`, который позволяет задавать кастомные функции для
генерации заголовков `Etag` и/или `Last-Modified`. В этих функциях можно реализовать более экономный способ определения
версии ресурса, например, на основе поля в БД, без необходимости генерации полного ответа view.

```python
# models.py

class Author(models.Model):
    ...
    updated_at = models.DateTimeField(auto_now=True)


# views.py
from django.views.decorators.http import condition


def author_updated_at(request, username):
    updated_at = Author.objects.filter(username=username).values_list('updated_at', flat=True)
    if updated_at:
        return updated_at[0]
    return None


@condition(last_modified_func=author_updated_at)
def author_page_view(request, username):
    ...
```

В функции `author_updated_at` выполняется простой запрос БД, который возвращает дату последнего обновления ресурса,
что требует значительно меньше ресурсов чем получение всех нужных данных для view из БД и рендеринг шаблона.
При этом при изменении автора функция вернет новую дату, что приведет к инвалидации кэша.

## Кэширование статических файлов

Для  ускорения повторной загрузки страниц рекомендуется включить кэширование статических файлов, чтобы браузер повторно
не запрашивал те же скрипты, стили, картинки и тд.

В продакшн окружении вы скорее всего не будете отдавать статические файлы через Django, т.к. это медленно и не безопасно.
Для этой задачи обычно используется Nginx или другой web-сервер. Рассмотрим как настроить кэширование статики на примере Nginx:

```nginx
server {
    # ...

    location /static/ {
        expires 360d;
        alias /home/www/proj/static/;
    }

    location /media/ {
        expires 360d;
        alias /home/www/proj/media/;
    }
}
```

Где,

-  `/static/` это базовый путь к статическим файлам, куда, в том числе, копируются файлы при выполнении `collectstatic`,
-  `/media/` базовый путь к файлам загружаемым пользователями.

В данном примере мы кэшируем всю статику на 360 дней. Важно, чтобы при изменении какого-либо статического файла, его
URL также изменялся, что приведет к загрузке новой версии файла. Для этого можно добавлять GET параметры к файлам с
номером версии: `script.js?version=123`. Но мне больше нравится использовать
[Django Compressor](https://django-compressor.readthedocs.io/en/latest/), который кроме всего прочего, генерирует
уникальное имя для скриптов и стилей при их изменении.
