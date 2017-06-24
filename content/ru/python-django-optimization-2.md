Title: Оптимизация производительности Django проектов (часть 2)
Slug: django-project-optimization-part-2
Date: 2017-06-24 10:50
Category: python
Tags: python, django
Lang: ru

Это продолженние серии статей про оптимизацию Django приложений. Первая часть доступна
[здесь](/ru/django-project-optimization-part-1/) и рассказывает о профилировании и настройках Django. В этой части
мы рассмотрим оптимизацию работы с БД (модели Django).

В этой части часто будет использоваться логирование SQL запросов, настройка которого описана в первой части серии.
В качестве БД во всех примерах будет использоваться PostgreSQL, но для пользователей других СУБД большая часть статьи
также будет актуальна.

Примеры в этой части будут основаны на простом приложении блога, которое мы будем разрабатывать и оптимизировать по
ходу статьи. Начнем с следующих моделей:

```python
from django.db import models


class Tag(models.Model):

    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Author(models.Model):

    username = models.CharField(max_length=64)
    email = models.EmailField()
    bio = models.TextField()

    def __str__(self):
        return self.name


class Article(models.Model):

    title = models.CharField(max_length=64)
    content = models.TextField()
    created_at = models.DateField()
    author = models.ForeignKey(Author)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title
```

Весь код доступен на [github](https://github.com/dizballanze/django-optimization-guide-2-sample/tree/initial)
с разбивкой по тегам.

## Массовые изменения

### Массовая вставка

Предположим, что наше новое приложение блога заменяет старое приложение и нам нужно перенести данные в новые модели.
Также предположим, что мы экспортировали данные из старого приложения в огромные json файлы. Файл с авторами следующего вида:

```json
[
  {
    "username": "mackchristopher",
    "email": "dcortez@yahoo.com",
    "bio": "Vitae mollitia in modi suscipit similique. Tempore sunt aliquid porro. Molestias tempora quos corporis quam."
  }
]
```

Сделаем команду Django для импортирования авторов из json файла:

```python
class Command(BaseCommand):

    help = 'Load authors from `data/old_authors.json`'

    DATA_FILE_PATH = os.path.join(settings.BASE_DIR, '..', 'data', 'old_data.json')

    def handle(self, *args, **kwargs):
        with open(self.DATA_FILE_PATH, 'r') as json_file:
            data = json.loads(json_file.read())
        for author in data:
            self._import_author(author)

    def _import_author(self, author_data):
        author = Author(
            username=author_data['username'],
            email=author_data['email'],
            bio=author_data['bio'])
        author.save()
```

Проверим сколько SQL запросов выполняется при загрузке 200 авторов. Используем `python manage.py shell`:

```python
from django.core.management import call_command
from django.db import connection
call_command('load_data')
print(len(connection.queries))
```

Этот код выведет множество SQL запросов (т.к. у нас включено их логирование), а в последней строке будет число `200`.
Это означает, что для каждого автора выполняется отдельный INSERT SQL запрос. Если у вас большое количество данных,
то такой подход может быть очень медленным. Воспользуемся методом `bulk_create` менеджера модели `Author`:

```python
    def handle(self, *args, **kwargs):
        with open(self.DATA_FILE_PATH, 'r') as json_file:
            data = json.loads(json_file.read())
        author_instances = []
        for author in data:
            author_instances.append(self._import_author(author))
        Author.objects.bulk_create(author_instances)

    def _import_author(self, author_data):
        author = Author(
            username=author_data['username'],
            email=author_data['email'],
            bio=author_data['bio'])
        return author
```

Запустив команду, описанным выше способом, мы увидем, что был выполнен один огромный запрос к БД!

>Если вам действительно нужно вставить большой объем данных, возможно придется разбить вставку на несколько запросов.
Для этого существует параметр `batch_size` у метода `bulk_create`, который задает максимальное количество объектов,
которые будут вставленны за один запрос. Т.е. если у нас 200 объектов, задав `bulk_size = 50` мы получим 4 запроса.

>У метода `bulk_size` есть ряд ограничений с которыми вы можете ознакомиться в [документации](https://docs.djangoproject.com/en/1.11/ref/models/querysets/#bulk-create).

### Массовая вставка M2M

Теперь нам нужно вставить статьи и теги, которые находятся в отдельном json файле с следующей структурой:

```json
[
  {
    "created_at": "2016-06-11",
    "author": "nichole52",
    "tags": [
      "ab",
      "iure",
      "iusto"
    ],
    "title": "...",
    "content": "..."
  }
]
```

Напишем для этого еще одну команду Django:

```python
class Command(BaseCommand):

    help = 'Load articles from `data/old_articles.json`'

    DATA_FILE_PATH = os.path.join(settings.BASE_DIR, '..', 'data', 'old_articles.json')

    def handle(self, *args, **kwargs):
        with open(self.DATA_FILE_PATH, 'r') as json_file:
            data = json.loads(json_file.read())
        for article in data:
            self._import_article(article)

    def _import_article(self, article_data):
        author = Author.objects.get(username=article_data['author'])
        article = Article(
            title=article_data['title'],
            content=article_data['content'],
            created_at=article_data['created_at'],
            author=author)
        article.save()
        for tag in article_data['tags']:
            tag_instance, _ = Tag.objects.get_or_create(name=tag)
            article.tags.add(tag_instance)
```

Запустив ее я получил 3349 SQL запросов! Многие из которых имели следующий вид:

```SQL
(0.001) SELECT "blog_article_tags"."tag_id" FROM "blog_article_tags" WHERE ("blog_article_tags"."article_id" = 2319 AND "blog_article_tags"."tag_id" IN (67)); args=(2319, 67)
(0.000) INSERT INTO "blog_article_tags" ("article_id", "tag_id") VALUES (2319, 67) RETURNING "blog_article_tags"."id"; args=(2319, 67)
(0.000) SELECT "blog_tag"."id", "blog_tag"."name" FROM "blog_tag" WHERE "blog_tag"."name" = 'fugiat'; args=('fugiat',)
(0.001) SELECT "blog_article_tags"."tag_id" FROM "blog_article_tags" WHERE ("blog_article_tags"."article_id" = 2319 AND "blog_article_tags"."tag_id" IN (68)); args=(2319, 68)
(0.000) INSERT INTO "blog_article_tags" ("article_id", "tag_id") VALUES (2319, 68) RETURNING "blog_article_tags"."id"; args=(2319, 68)
(0.000) SELECT "blog_tag"."id", "blog_tag"."name" FROM "blog_tag" WHERE "blog_tag"."name" = 'repellat'; args=('repellat',)
(0.001) SELECT "blog_article_tags"."tag_id" FROM "blog_article_tags" WHERE ("blog_article_tags"."article_id" = 2319 AND "blog_article_tags"."tag_id" IN (58)); args=(2319, 58)
(0.000) INSERT INTO "blog_article_tags" ("article_id", "tag_id") VALUES (2319, 58) RETURNING "blog_article_tags"."id"; args=(2319, 58
```

Добавление каждого тега к статье выполняется отдельным запросом. Это можно улучшить передавая методу `article.tags.add`
сразу список тегов:

```python
    def _import_article(self, article_data):
        # ...
        tags = []
        for tag in article_data['tags']:
            tag_instance, _ = Tag.objects.get_or_create(name=tag)
            tags.append(tag_instance)
        article.tags.add(*tags)
```

Этот вариант отправляет 1834 запроса, почти в 2 раза меньше, неплохой результат учитывая что мы изменили всего лишь
пару строк кода.

### Массовое изменение
