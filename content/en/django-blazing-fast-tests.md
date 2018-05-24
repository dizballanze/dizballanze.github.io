Title: Blazing fast tests in Django
Slug: django-blazing-fast-tests
Date: 2018-05-24 11:27
Author: Admin
Lang: en

Slow tests not only waste developers time on waiting but also make it difficult to follow TDD best practices
(such as red-green testing). If it needs minutes or even longer to run test suit, it leads to infrequent whole suit run.
Which in its turn leads to late bugs discovery and fix.

In this post, I'll tell how to speed up tests of your Django application. Also, I'll describe what kills your tests
performance. I will use simple tests suit as an example in this post. You can find it
[on GitHub](https://github.com/dizballanze/blazing-fast-django-tests-example/tree/initial).


## Parallel testing

The most simple way to speed up tour tests without the need to make any code changes - run tests in parallel.
Django provides `--parallel` option for running tests in parallel. This parameter also accepts an optional number of
processes. If this number wasn't provided it uses processes count equal to count of processor cores. For most of the
cases, this is optimal.

Sequential running of tests from [the example](https://github.com/dizballanze/blazing-fast-django-tests-example/tree/initial)
on my machine:

```
# python manage.py test
...........
----------------------------------------------------------------------
Ran 11 tests in 8.012s
```

Let's try to use `--parallel` option:

```
# python manage.py test --parallel
...........
----------------------------------------------------------------------
Ran 11 tests in 2.628s
```

As you can see tests completed more than 3 times faster.

> It's worth noting that Django distributes execution of different test cases between different processes. Consequently,
if you have fewer test cases then processor cores Django will decrease the count of processes to match count of test cases.
In our example, we have only 3 test cases, so parallelism is limited to 3 processes. On real projects you probably
have hundreds or even thousands of test cases and this problem won't touch you.

> In some cases Django can't collect tracebacks on tests failures in parallel mode. In that case, you need to re-run
tests sequentially.


## Use weak passwords hashing algorithm

By default, Django uses a computationally difficult algorithm for passwords hashing. Regularly in new Django versions,
the hashing algorithm is reinforced. It needs for security, so intruder will need a lot of computing power to break passwords.

We don't need such a strong algorithm in tests. We can go with something faster, such as MD5.
Let's add switching to MD5 for tests to `settings.py`:

```
import sys

TESTING = 'test' in sys.argv

if TESTING:
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]
```

And run tests again:

```
# python manage.py test --parallel
...........
----------------------------------------------------------------------
Ran 11 tests in 0.564s
```

4.65x times faster 🚀 I saw how this simple hack accelerated huge test suit by an order of magnitude.


## Create data only when we need it

A frequent mistake that slows down tests execution is to have a base test case with huge `setUp` method that creates data
for the whole test suit. At first sight, it may seem convenient, but it kills your tests performance because
**all** data are created before **each** test no matter if you need them in this particular test or not.

To fix this problem you need to simplify `setUp` method. Ideally fully remove `setUp` method from the base test case.
Test data should be created in particular test cases only when they are needed.

I added [corresponding changes](https://github.com/dizballanze/blazing-fast-django-tests-example/commit/45d89a2ee690e5077a7d957acd77aa4ceb1c41b8)
to our example. Let's see how this will affect tests running time:

```
# python manage.py test --parallel
...........
----------------------------------------------------------------------
Ran 11 tests in 0.353s
```

That's 60% more speed up.


## setUpTestData

Base Django test case allows creating test data on the level of the test case instead of the test method. This allows
vastly accelerate tests execution. You need to move data creation to class method `setUpTestData`.

> Objects created in `setUpTestData` shouldn't change while test running because it can lead to instability due to
not fully isolated tests.


I added changes to the example
[here](https://github.com/dizballanze/blazing-fast-django-tests-example/commit/5594cac4fd93c699b572f6946ce0a04ad96495f5).
Let's run tests again:

```
# python manage.py test --parallel
...........
----------------------------------------------------------------------
Ran 11 tests in 0.349s
```

Seems that we don't get the significant speed up. Let's see what's happen if we add
[some more tests](https://github.com/dizballanze/blazing-fast-django-tests-example/commit/c865ff7f72b04a0f72e8edfe3c523f1ee00b923e).
Without `setUpTestData` I get `0.536s` duration and with `setUpTestData` - `0.348s`. As you can see with `setUpTestData`
duration doesn't grow on adding new tests (besides duration of running the test itself) because test data aren't created
before each test.


## Conclusion

It's desirable to pay attention to the speed of the tests from the very beginning of the development. Using simple methods
you can get very fast tests and get maximum benefit from automatic testing.

live long and prosper 🖖
