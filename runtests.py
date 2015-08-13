#!/usr/bin/env python
import sys
import django
from django.conf import settings, global_settings as default_settings
from django.core.management import execute_from_command_line

if not settings.configured:
    settings.configure(
        DATABASES = {
            'default': {'ENGINE': 'django.db.backends.sqlite3','NAME': ':memory:',},  # Django 1.4 wants this.
        },
        TEMPLATE_LOADERS = (
            'django.template.loaders.app_directories.Loader',
        ),
        TEMPLATE_CONTEXT_PROCESSORS = default_settings.TEMPLATE_CONTEXT_PROCESSORS + (
            'django.core.context_processors.request',
        ),
        INSTALLED_APPS = (
            'tag_parser',
        ),
        MIDDLEWARE_CLASSES = (),
        TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner' if django.VERSION < (1,6) else 'django.test.runner.DiscoverRunner',
    )

DEFAULT_TEST_APPS = ['tag_parser']


def runtests():
    other_args = list(filter(lambda arg: arg.startswith('-'), sys.argv[1:]))
    test_apps = list(filter(lambda arg: not arg.startswith('-'), sys.argv[1:])) or DEFAULT_TEST_APPS
    argv = sys.argv[:1] + ['test', '--traceback'] + other_args + test_apps
    execute_from_command_line(argv)

if __name__ == '__main__':
    runtests()
