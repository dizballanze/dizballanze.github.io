Title: Django project optimization guide (part 1)
Date: 2017-6-14 16:47
Author: Admin
Category: Python
Tags: python, django, performance, load testing
Lang: en


Django is a powerfull framework used in many of great projects. It's provide many batteries, that speed up development and
therefore reduce the price of it. When project becomes large and uses by many users you inevitebly will run into performance
problem. In this guide I will try to explain what problems may occur and how to fix them.


## Profiling

Before start to make any optimizations you should measure current performance characteristics to be able to compare results of 
optimizations. And you should be able to measure performance regulary after each changes, so this process should be automized.

Profiling is a process of measurement metrics of your project. Such as: server response time, CPU usage, memory usage, etc.
Python has it's own [profiler](https://docs.python.org/3/library/profile.html) in standard library. It's pretty good
in profiling code chunks, but for profiling a whole django project exists more convenient solutions.


### Django logging

One of the most common optimization issue is a needles and/or not effective SQL queries. You could set up Django logging to
display all SQL queries to a console. Add to `settings.py` file:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    },
}
```

also, make sure that `DEBUG = True`. After reloading server you should see SQL queries and corresponding time in console
for every request you make:

![SQL logging](/media/2017/6/sql-logging.png)

### Django Debug Toolbar

[This](http://django-debug-toolbar.readthedocs.io/en/stable/) django application provide a set of toolbars, some of
which is great for profiling. Actually it has built-in SQL panel, that has even more informative log of SQL queries
with additional features, like time chart, traceback, result of `EXPLAIN` command, etc.


![DDT](/media/2017/6/ddt.png)

Also, DDT has non-default built-in profiling panel. It provides web interface to profiling results of the current request.
To enable it, you should add `debug_toolbar.panels.profiling.ProfilingPanel` to `DEBUG_TOOLBAR_PANELS` list in `settings.py.

![DDT profiling panel](/media/2017/6/ddt-profiling-panel.png)


### Profiling data

Very important to use production-like data for profiling. Ideally you should grab a dump from production database and use it
on your local machine. If you try to measure performance on empty/small database you can receive wrong results, that doesn't
help you to optimize project correctly.


## Load testing

After optimizations you should make load testing to make sure that performance is on sufficient level to work on production
load. For this type of testing you need to setup copy of your production environment. Hopefully cloud services and
deploy automation allow us to make such setup in minutes.

I recommend to use [Locust](http://locust.io/) for load testing. It's main feature is that you describe all your tests in
plain Python code. You could setup sophisticated load scenarios that would be close to real users behavior. Example of
`locustfile.py`:

```python
from locust import HttpLocust, TaskSet, task


class UserBehavior(TaskSet):
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        self.login()

    def login(self):
        self.client.post("/login", {"username":"ellen_key", "password":"education"})

    @task(2)
    def index(self):
        self.client.get("/")

    @task(1)
    def profile(self):
        self.client.get("/profile")


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
```

Also, Locust provide web-interface to run tests and see results:

![Locust web interface](/media/2017/6/locust-screenshot.png)

Best thing, that you can setup Locust once and use it to verify project performance after every change. Maybe you could even
add it to your CI/CD pipeline!


## Django settings

In this section I will discribe Django settings, that may affect performance.


### Database connection lifetime

by changing [`CONN_MAX_AGE`](https://docs.djangoproject.com/en/1.11/ref/settings/#conn-max-age) value:

-  `0` - close connection at the end of each request,
-  `> 0` - TTL in seconds,
-  `None` - unlimited TTL.


```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydatabase',
        'USER': 'mydatabaseuser',
        'PASSWORD': 'mypassword',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'CONN_MAX_AGE': 60 * 10,  # 10 minutes
    }
}
```

### Templates caching

If you use Django version less than 1.11 you should consider to enable templates caching. By default Django (<1.11) reads
from file system and compliles templates every time they're rendered. You could use `django.template.loaders.cached.Loader`
to enable templates caching in memory. Add to `settings.py`:


```
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'foo', 'bar'), ],
        'OPTIONS': {
            # ...
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]
```

### Redis cache backend

Django provide several built-in cache backends, such as database backend, file based backend, etc. I recommend to store
your cache in Redis - popular in-memory data structure store, probably you already use it in your project.
To setup Redis as cache backend you need to use third-party package, e.g. `django-redis`.

Install django-redis with pip:

```
pip install django-redis
```

Устанавливаем django-redis при помощи pip:

```
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```

Read full documentation [here](http://niwinz.github.io/django-redis/latest/).


### Sessions backend

By default Django stores sessions in database. To speed up this we can store sessions in cache. Add to `settings.py`:

```
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```

### Remove unneede middlewares

Check list of middlewares (`MIDDLEWARE` in `settings.py`). Make sure you need all of them and remove unneeded.
Django call each middleware for each processed request, so overhead can be significant.

If you have custom middleware, that used only in segment of requests, you could try to move this functionality to
view mixin or decorator. So over endpoint will not have overhead of this middleware.
