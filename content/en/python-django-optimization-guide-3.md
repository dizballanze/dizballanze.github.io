Title: Django project optimization guide (part 3)
Slug: django-project-optimization-part-3
Date: 2017-09-18 09:00
Category: python
Tags: python, django
Lang: en


Other parts of this guide:

-  [Part 1. Profiling and Django settings](/en/django-project-optimization-part-1)
-  [Part 2. Working with database](/en/django-project-optimization-part-2/)
-  Part 3. Caching

In this part of the guide, I will cover the most valuable approach to achieve high performance - caching.
The essence of caching is that you place the most commonly used data to fast storage in order to speed up the access to them.
It's important to understand that the fast storage (i.e. memory) often has limited capacity. So we should use it only for
that data which will be often used.


## Django cache framework

Django has different built-in cache features. Cache storage can be set up with `CACHES` dict in `settings.py`:

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "my_cache_table",
    }
}
```

Django has several built-in cache backends. Let's check some of them:

-  `DummyCache` - caches nothing, is used in development or testing environments to temporary disable caching,
-  `DatabaseCache` - stores cache in the database. Not very fast storage, but can be useful to store results of long
calculations or difficult database queries.
-  `MemcachedCache` uses [Memcached](http://memcached.org/) as cache storage. You need to have Memcached server(s) to
use this backend.

`MemcachedCache` is the most suitable backend for production usage. `DatabaseCache` also can be useful in specific cases.
Also, Django supports 3rd-party backends, for example, Redis can be a good option as cache backend. Redis
provides [more features](http://antirez.com/news/94) than Memcached and it's quite possible that you're already using
it in your project. You can install `django-redis` package and
[configure](http://niwinz.github.io/django-redis/latest/#_configure_as_cache_backend) it as a cache backend.

### The per-site cache

If you don't have any dynamic content on your project, you can simply solve the cache problem - enabling
the per-site caching. You need to add several changes to your `settings.py` for this:

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

As you can see, you should add middlewares at the beginning and at the end of `MIDDLEWARE` list. After that, all GET and HEAD
requests will be cached for `CACHE_MIDDLEWARE_SECONDS` seconds.

You can also clear cache programmatically:

```python
from django.core.cache import caches
cache = caches['default']  # `default` is a key from CACHES dict in settings.py
ache.clear()
```

Or you can clean cache directly in the cache storage if necessary. An example for Redis:


```
$ redis-cli -n 1 FLUSHDB # 1 is a DB number specified in settings.py
```

###  The per-view caching

In case it's not appropriate to cache the whole site, you can enable caching only for specific views (i.e. most highly used).
Django provides `cache_page` decorator for this:

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

`cache_page` accepts following arguments:

-  first, required argument is a time-to-live of cache in seconds,
-  `cache` - key from `CACHES` dict,
-  `key_prefix` - cache key prefix.

Also, you can apply this decorator in `urls.py`, that is convenient for Class-Based Views:

```python
urlpatterns = [
    url(r'^$', cache_page(600)(ArticlesListView.as_view()), name='articles_list'),
    ...
]
```

If for example page content changes are based on authenticated user, then this approach won't work. To solve this
problem you should use one of the approaches described below.

### Template fragment caching

In the previous part of this guide, I mentioned that QuerySet objects are lazy and SQL requests are delayed as long as possible.
We can take the advantage of this and cache template fragments, that will let us to avoid SQL requests for cache TTL. `cache` template
tag is provided for this:

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

The result of adding `cache` template tags to our template (before and after respectively):

![django-templates-caching-results](/media/2017/8/templates-caching.png)

`cache` accepts following arguments:

-  first required argument is a TTL of cache,
-  the second required argument is a fragment name,
-  optional additional variables which identify fragment by dynamic data,
-  keyword `using='default'` argument, should correspond to a key in `CACHES` dict.

For example, we need to cache each template fragment separately for different users.
Let's provide an additional variable that identifies a user to `cache` template tag:

```html
{% cache 500 personal_articles_list request.user.username %}
    <!-- ... -->
{% %}
```

You can even provide several additional variables like this to create caching key based on a combination of their values.

### The low-level caching

Django provides access to the low-level caching API. You can use it to save/extract/delete data by specified cache key.
Let's check out a small example:

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

In this code fragment, we check whether authors count is in the cache by `authors_count` key. `cache.get` method returns
not `None` value if the key exists in the cache storage. In that case, we can use this value without any requests to the database.
Otherwise, code requests authors count from the database and saves it in the cache. In this way, we avoid database requests for
a cache TTL. 

Besides database queries results, it makes sense to cache results of complex calculations or requests to external services.
It's important to understand that data can change and cache will contain stale information. There are several approaches to minimize
a chance to use stale data from cache:

-  set up cache TTL to correspond frequency of data change,
-  add cache invalidation.

Cache invalidation should happen on data change. Let's check out how to add cache invalidation for authors count
example:

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

In this example 2 signal handlers on adding/deleting of authors were added. That makes possible to remove cache by
`authors_count` key on authors quantity change and the new number of authors will be fetched from the database.

## cached_property

Besides of cache framework, Django provides an ability to cache methods' invocations right in the process memory. This type of caching
is possible only for methods without arguments (besides of `self`). This type of cache will live while the corresponding instance exists.

`cached_property` is included Django decorator. Methods with this decorator also become properties. Let's check out
an example:

```python
class Author(models.Model):

    username = models.CharField(max_length=64, db_index=True)
    email = models.EmailField()
    bio = models.TextField()

    @cached_property
    def articles_count(self):
        return self.articles.count()
```

Let's check how the `article_count` property works with enabled SQL logging:

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

As you can see, repeated access to the `article_count` property doesn't cause any SQL requests. But if we create another
instance of this `Author` class, this property won't be cached until first access to it. That's because the cache is tied
to the specific instance of `Author` class.

## Cacheops

[django-cacheops](https://github.com/Suor/django-cacheops) is a 3rd party package, that allows you quickly enable caching
of database requests almost without code changes. You can solve most of the caching cases just by setting up the package in
`settings.py`.

Let's check an example of simple cacheops usage. As a test project, I will use the
[sample project](https://github.com/dizballanze/django-optimization-guide-2-sample) from the previous part of this guide.

Cacheops is using Redis as a cache storage, so we need to setup Redis connection parameters in `settings.py`.

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

Just like that, we added caching of all databases requests from all models of `blog` application for 15 minutes.
As a bonus cacheops provides automatic cache invalidation for not only time-based but also event-based by setting up
model signals of corresponding models.

If necessary, you can setup caching more accurate and specify it per model and per request type settings.
Few examples:

```python
CACHEOPS = {
    'blog.author': {'ops': 'all', 'timeout': 60 * 60},  # cache all queries to `Author` model for an hour

    'blog.article': {'ops': 'fetch', 'timeout': 60 * 10},  # cache `Article` fetch queries for 10 minutes
    # Or
    'blog.article': {'ops': 'get', 'timeout': 60 * 15},  # cache `Article` get queries for 15 minutes
    # Or
    'blog.article': {'ops': 'count', 'timeout': 60 * 60 * 3},  # cache `Article` fetch queries for 3 hours

    '*.*': {'timeout': 60 * 60},
    '*.*': {'timeout': 60 * 60},
}
```

Besides that, cacheops also has several useful features:

-  manual caching by `QuerySet` method: `Article.objects.filter(tag=2).cache()`,
-  function results caching with bounding to models and automatic invalidation,
-  views caching with models bounding and automatic invalidation,
-  template fragments caching and more.

You should check out [cacheops' README](https://github.com/Suor/django-cacheops/blob/master/README.rst) for details.

## HTTP caching

If your project uses HTTP, you should consider using built-in cache capabilities in HTTP protocol. They allow cache
results of safe requests (GET and HEAD) on a client (i.e. browser) and on intermediate proxy servers.

Caching control is performed by HTTP headers. You can setup these headers in application or web server (Nginx, Apache, etc).

Django provides several convenient middlewares and view decorators to control HTTP caching.

### Vary

The [`Vary`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Vary) header allows to specify a list of header names,
which values will be used to create cache keys. Django provides view decorator
[`vary_on_headers`](https://docs.djangoproject.com/en/1.11/topics/cache/#using-vary-headers) for control of this header.

```python
from django.views.decorators.vary import vary_on_headers


@vary_on_headers('User-Agent')
def author_page_view(request, username):
    ...
```

In this case, different cache keys will be used for different values of `User-Agent` header.

### Cache-Control

The [`Cache-Control`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control) header is used to control
how caching is performed.
[`cache_control`](https://docs.djangoproject.com/en/1.11/topics/cache/#controlling-cache-using-other-headers)
view decorator allows setting this header directives.

```python
from django.views.decorators.cache import cache_control


@cache_control(private=True, max_age=3600)
def author_page_view(request, username):
    ...
```

Let's check out some `Cache-Contol` directives:

-  `public`, `private` - allows or forbids caching in public caches (proxy servers, etc). This is an important directive
because it allows securing private content that should be available only for specific users.
-  `no-cache` - disables caching that makes a client to perform a request to the origin server.
-  `max-age` - after that time (in seconds) cache is considered stale.

### Last-Modified & Etag

HTTP protocol provides more complicated caching capabilities which allow verifying data freshness by the server with
conditional requests. To make this capabilities work server should provide one or both of the following headers:

-  `Last-Modified` - date and time of last resource modification,
-  `Etag` - resource version identifier (hash or version number)

After that, client should provide `If-Modified-Since` and `If-None-Match` headers on following requests.
Server checks if the resource wasn't changed since the last request and returns 304 response without the body.
This allows to perform repeated resource that loads only if it was changed. In this way it saves time and server resources.

Besides caching, described capabilities are used to precondition checking in unsafe requests (POST, PUT, etc).
But this is beyond the topic of this guide.

Django provides several ways to control `ETag` and `Last-Modified` headers. The simplest one is to use
`ConditionalGetMiddleware`. This middleware based on view response adds `Etag` header to all GET requests.
Also, it checks request headers and returns 304 if the resource wasn't changed.

This approach has several drawbacks:

-  middleware is applied to all views of the project, that sometimes isn't necessary,
-  it generates full response to get resource version, that requires lots of server resources,
-  it works only for GET requests.

There is more accurate approach, you should use `condition` view decorator, that allows specifying custom
functions to generate `Etag` and/or `Last-Modified` headers. In this functions, you can use more effective
approach of detecting resource version. You can just request one field from the database with no need to generate
a full response.

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

`author_updated_at` function performs simple database request, that returns resource's last update date. This is more
efficient than fetching all necessary data from the database and rendering a template. After any changes to author
are done the function returns new date that will lead to cache invalidation.

## Static files caching

You should cache static files to speed up repeated pages loading. This will prevent browser from repeated loading of
scripts, styles, images, etc.

Most likely you won't serve static files by Django in a production environment, because it's slow and unsafe.
Usually, web server is used for this task, i.e. Nginx. Let's check out how to set up caching of static files with Nginx:

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

Where,

-  `/static/` base path to static files, it's the same place where `collectstatic` copies files,
-  `/media/` base path to user generated files.

In this case, we cache all static for 360 days. It's important that URL of static files are changed when files are
changed. This will lead to loading of a new version of the file. You can use GET parameters with version numbers:
`script.js?version=123`. But I prefer using [Django Compressor](https://django-compressor.readthedocs.io/en/latest/),
that generates unique file names for all scripts and styles on each change.
