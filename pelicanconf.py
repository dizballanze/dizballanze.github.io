#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Yuri Shikanov'
SITENAME = 'Tech blog by @dizballanze'
SITEURL = 'http://dizballanze.com'
FEED_DOMAIN = SITEURL

PATH = 'content'

TIMEZONE = 'Europe/Moscow'

DEFAULT_LANG = 'en'

# Blogroll
MENUITEMS  =  (
    ('WB–Tech', 'https://wbtech.pro/'),
    ('DebugMail', 'https://debugmail.io/'),)

# Social widget
SOCIAL = (('Twitter', 'https://twitter.com/dizballanze'),
          ('GitHub', 'https://github.com/dizballanze'),)

DEFAULT_PAGINATION = False

ARTICLE_URL = u'{slug}/'
ARTICLE_SAVE_AS = u'{slug}/index.html'
PAGE_URL = u'{slug}/'
PAGE_SAVE_AS = u'{slug}/index.html'
AUTHOR_URL = u'author/{slug}/'
AUTHOR_SAVE_AS = u'author/{slug}/index.html'
CATEGORY_URL = 'category/{slug}.html'
CATEGORY_SAVE_AS = 'category/{slug}.html'

TAG_URL = u'tag/{slug}/'
TAG_SAVE_AS = u'tag/{slug}/index.html'

GITHUB_URL = 'https://github.com/dizballanze'
TWITTER_USERNAME = 'dizballanze'

# MARKDOWN = {
    # 'extra': {},
    # 'toc': {}
# }

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

STATIC_PATHS = ['icons', 'media', 'stuff', ]

EXTRA_PATH_METADATA = {
    'stuff/robots.txt': {'path': 'robots.txt'},
    'stuff/CNAME': {'path': 'CNAME'}
}

# CSS_FILE = "app.css"
THEME = './basic-theme'


PLUGIN_PATHS = 'plugins'
PLUGINS = ['i18n_subsites', 'pelican-toc']


I18N_UNTRANSLATED_ARTICLES = 'hide'


I18N_SUBSITES = {
    'en': {
        'SITENAME': SITENAME,
    },
    'ru': {
        'SITENAME': SITENAME,
    }
}

DATE_FORMATS = {
    'en': ('en_US','%d %b %Y'),
    'ru': ('ru_RU','%d %b %Y'),
}
