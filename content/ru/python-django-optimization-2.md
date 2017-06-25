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

После переноса данных пришла идея, что к старые статьи (раньше 2012 года) нужно запретить комментировать. Для этого
было добавлено логическое поле `comments_on` к моделе `Article` и нам необходимо проставить его значение:

```python
from django.db import connection
from blog.models import Article
for article in Article.objects.filter(created_at__year__lt=2012):
    article.comments_on = False
    article.save()
print(len(connection.queries))
```

Запустив этот код я получил 179 запросов следующего вида:

```sql
(0.000) UPDATE "blog_article" SET "title" = 'Saepe eius facere magni et eligendi minima sint.', "content" = '...', "created_at" = '1992-03-01'::date, "author_id" = 730, "comments_on" = false WHERE "blog_article"."id" = 3507; args=('Saepe eius facere magni et eligendi minima sint.', '...', datetime.date(1992, 3, 1), 730, False, 3507)
```

Кроме того, что для каждой статьи подходящей по условию происходит отдельный SQL запрос, еще и все поля этих статей
перезаписываются. А это может привести к перезаписи изменений сделанных в промежутке между SELECT и UPDATE запросами.
Т.е. кроме проблем с производительностью мы также получаем race condition.

Вместо этого мы можем использовать метод `update` доступный у объектов `QuerySet`:

```python
Article.objects.filter(created_at__year__lt=2012).update(comments_on=False)
```

Этот код генерирует всего один SQL запрос:

```sql
(0.004) UPDATE "blog_article" SET "comments_on" = false WHERE "blog_article"."created_at" < '2012-01-01'::date; args=(False, datetime.date(2012, 1, 1))
```

Если для изменения полей нужна сложная логика, которую нельзя реализовать полностью в update операторе, можете вычислить
значение поля в python коде и затем использовать один из следующих вариантов:

```python
Model.object.filter(id=instance.id).update(field=computed_value)`
# or
instance.field = computed_value
instance.save(update_fields=('fields',))
```

Но оба эти варианта также страдают от race condition, хоть и в меньшей степени.

### Массовое удаление объектов

Допустим, что нам потребовалось удалить все статьи отмеченные тегом `minus`:

```python
from django.db import connection
from blog.models import Article
for article in Article.objects.filter(tags__name='minus'):
    article.delete()
print(len(connection.queries))
```

Код сгенерировал 93 запроса следующего вида:

```sql
(0.000) DELETE FROM "blog_article_tags" WHERE "blog_article_tags"."article_id" IN (3510); args=(3510,)
(0.000) DELETE FROM "blog_article" WHERE "blog_article"."id" IN (3510); args=(3510,)
```

Сначала удаляется связь статьи с тегом в промежуточной таблице, а затем и сама статья. Мы можем сделать это за
меньшее количество запросов, используя метод `delete` класса `QuerySet`:

```python
from django.db import connection
from blog.models import Article
Article.objects.filter(tags__name='minus').delete()
print(len(connection.queries))
```

Этот код выполняет то же самое всего за 3 запроса к БД:

```sql
(0.004) SELECT "blog_article"."id", "blog_article"."title", "blog_article"."content", "blog_article"."created_at", "blog_article"."author_id", "blog_article"."comments_on" FROM "blog_article" INNER JOIN "blog_article_tags" ON ("blog_article"."id" = "blog_article_tags"."article_id") INNER JOIN "blog_tag" ON ("blog_article_tags"."tag_id" = "blog_tag"."id") WHERE "blog_tag"."name" = 'minus'; args=('minus',)
(0.002) DELETE FROM "blog_article_tags" WHERE "blog_article_tags"."article_id" IN (3713, 3717, 3722, ...); args=(3713, 3717, 3722, ...)
(0.001) DELETE FROM "blog_article" WHERE "blog_article"."id" IN (3713, 3717, ...); args=(3713, 3717, 3722, ...)``sql
```

Сначала одним запросом получается список идентификаторов всех статей отмеченных тегом `minus`, затем первый запрос
удаляет связи сразу всех этих статей с тегами и последний запрос удаляет статьи.

## Iterator

Предположим нам нужно добавить возможность экспорта статей в csv формат. Сделаем для этого простую команду Django:

```python
class Command(BaseCommand):

    help = 'Export articles to csv'

    EXPORT_FILE_PATH = os.path.join(settings.BASE_DIR, '..', 'data', 'articles_export.csv')
    COLUMNS = ['title', 'content', 'created_at', 'author', 'comments_on']

    def handle(self, *args, **kwargs):
        with open(self.EXPORT_FILE_PATH, 'w') as export_file:
            articles_writer = csv.writer(export_file, delimiter=';')
            articles_writer.writerow(self.COLUMNS)
            for article in Article.objects.select_related('author').all():
                articles_writer.writerow([getattr(article, column) for column in self.COLUMNS])
```

Для тестирования этой команды я сгенерировал около 100Мb статей и загрузил их в БД. Далее я запустил команду через профайлер
памяти [memory_profiler](https://pypi.python.org/pypi/memory_profiler).

```
mprof run python manage.py export_articles
mprof plot
```

В результате я получил следующий график по использованию памяти:

![export articles profiling](/media/2017/6/export_articles_without_iterator.png)

Команда использует около 250Mb памяти, потому что при выполнении запроса QuerySet получает из БД сразу все статьи и
кэширует их в памяти, чтобы при последующем обращении к этому QuerySet дополнительные запросы не выполнялись.
Мы можем уменьшить объем используемой памяти используя метод `iterator` класса `QuerySet`, который позволяет получать
результаты по одному используя server-side cursor и при этом он отключает кэширование результатов в QuerySet:

```python
# ...
for article in Article.objects.select_related('author').iterator():
# ...
```

Запустив обновленный пример в профайлере я получил следующий результат:

![export articles profiling](/media/2017/6/export_articles_with_iterator.png)

Всего лишь 50Mb! Также приятным побочным эффектом является то, что при любом размере данных, при использовании `iterator`,
команда используем постоянный объем памяти. Вот график для ~200Mb статей (без `iterator` и с ним соответственно):

![huge export articles profiling](/media/2017/6/export_articles_huge_before_and_after.png)
