Title: Pay attention to the code coverage report
Slug: test-coverage-report-in-use
Date: 2018-04-29 12:28
Author: Admin
Lang: en

If you are reading this post, you probably write unit-tests (and that's a good thing). Also, with high probability you
have heard about **code coverage** metric. Which shows what code has run during testing. But how often do you actually
look at code coverage report? If not too often, when this post is for you. I'll try to show you how code coverage
report opens a lot of useful data for developers, which in the end allows improving code quality.


## Testing

### Code without tests

Most obvious benefit from code coverage report is an ability to detect which code isn't testing. Often this means that
you need to add a test(s) for this code to make sure that it works properly. And which is no less important, that it
will continue to work properly with further application development.

Sometimes you can think, that one or the other code section is too simple and can't have any bugs. Accordingly,
you can avoid wasting time writing tests for it. In this moments you shouldn't forget, that code is changing and every
change may cause [regression](https://en.wikipedia.org/wiki/Software_regression). Each test can save you from hours of
debugging.

### Running of not expected code bug

Another case then a test passed but coverage report shows that code, that you expected to run, actually haven't run.

This may occur due to a bug in a test. Another function is used instead of the right one, which returns the same result.
A bug like this leads to false sense of confidence, that code is working and regressions are tracked which isn't true.
Finally, it may cause deploying of broken code to the production and you'll have a hard time to debug this.

The same result can be because of a bug in the code. For example, misconfigured web-application routing sends requests
to the wrong method, which occasionally returns expected response. This may lead to deploying the broken code to the
production and that would be hard to find this bug relying only on tests.

Reviewing code coverage report before sending changes to the repository, you can find such kind of bugs and prevent
them before they cause damage, not to mention the time savings.

## Dead code

### Unused code

In some cases, code coverage report can help you to find code which isn't used anymore. For example, private methods,
which aren't called anywhere.

There is nothing pleasant about wasting time on reading a dead code and trying to understand why it is needed. Code
like this should be removed promptly. If you think you may need this code in future - still remove it. You can restore
it from version control system if needed.

### Dead code in tests

Another less obvious example of dead code - dead code in tests. You can have a test method in which you're looping over
a list of some objects and make asserts on each of them. If the list for some reason turns out to be empty, the test
will pass although none of the asserts actually occur. This kind of bugs is easy to discover with code coverage report
because loop body will be shown as not covered.

## Conclusion

Code coverage report is a very important tool for a developer. You should look into the report after each change.
Ideally, this should be a part of your CI pipeline. If covered lines number was increased build should fail. Or at
least you should get a warning about this. This allows to avoid many bugs and increase overall code health.
