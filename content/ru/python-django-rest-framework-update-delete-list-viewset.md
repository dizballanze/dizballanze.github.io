Title: Обработка нестандартных HTTP методов в списках сущностей в Django Rest Framework
Slug: django-rest-framework-delete-put-patch-actions-on-list
Date: 2018-01-05 16:03
Category: python
Tags: python, django, django rest framework
Lang: ru


Т.к. не смог сам нагуглить решение этого вопроса, решил написать небольшую заметка о том, как сделать обработку
DELETE/PUT/PATCH запросов к списку сущностей через ViewSet в Django Rest Framework. По-умолчанияю, DRF ограничивает
запросы к списку сущностей в ViewSet методами GET для получения списка и POST для создания сущности.

За формирование списка маршрутов для ViewSet отвечает Router. Это происходит когда в `urls.py` вы пишите, что-то вроде:

```python
router = routers.DefaultRouter()
router.register(r'messages', MessagesViewSet, base_name='messages')

urlpatterns = [
    path('api/', (router.urls, 'api', 'api')),
]
```

Список маршрутов строится из 2х частей:

-  Заренее известных стандартных маршрутов, например, получение списка сущностей `GET /users/john-doe/messages` или
удаление определенной сущности `DELETE /users/john-doe/messages/42`. 
-  Кастомных маршуртов заданных при помощи декораторов `@detail_route` и `@list_route`.

Для того, чтобы добавить возможность обработки дополнительных HTTP методов к стандартным маршрутам viewset, нужно
дополнить соответствие HTTP методов к методам ViewSet класса, которое определено в атрибуте `routes`
класса `SimpleRouter`.

Для примера добавим возможность выполнять DELETE запросы к списку сущностей. Это может быть удобно, если ViewSet
отвечает за обработку дочерних сущностей к основной и мы хотим иметь возможность удаления всех дочерних сущностей
одним HTTP запросом.

Создадим подкласс `DefaultRouter` и переопределим в нем атрибут routes:

```python
from rest_framework import routers


class MyRouter(routers.DefaultRouter):

    routes = [
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                'post': 'create',
                'delete': 'destroy_list'
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        DynamicListRoute(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]
```

Здесь мы добавили новый маршрут `'delete': 'destroy_list'`, все остальное также как в родительском классе. В `urls.py`
нужно заменить создание стандартного роутера на `MyRouter`. Теперь для обработки DELETE запросов на
список сущностей нужно в ViewSet добавить метод `destroy_list`:

```
from rest_framework import viewsets, status


class UsersMessagesViewSet(viewsets.ModelViewSet):

    ...

    def destroy_list(self, request, *args, **kwargs):
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

В случае, если в ViewSet классе не будет этого метода на запросы будут просто возвращать
`405 Method not allowed`.

По аналогии можно добавить обработку PUT/PATCH в списки сущностей или даже других кастомных HTTP методов.
