#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Yuri Shikanov'
SITENAME = 'Tech blog by @dizballanze'
SITEURL = 'http://dizballanze.com'
FEED_DOMAIN = SITEURL

PATH = 'content'

TIMEZONE = 'Europe/Moscow'

DEFAULT_LANG = 'ru'

# Blogroll
LINKS =  (('WBTech', 'http://wbtech.pro'),)

# Social widget
SOCIAL = (('Twitter', 'https://twitter.com/dizballanze'),
          ('GitHub', 'https://github.com/dizballanze'),)

DEFAULT_PAGINATION = 10

ARTICLE_URL = u'{category}/{slug}/'
ARTICLE_SAVE_AS = u'{category}/{slug}/index.html'
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

# https://github.com/getpelican/pelican-plugins
MD_EXTENSIONS = ['toc', 'extra']

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

STATIC_PATHS = ['icons', 'media', 'stuff', ]

EXTRA_PATH_METADATA = {
    'stuff/robots.txt': {'path': 'robots.txt'},
    'stuff/CNAME': {'path': 'CNAME'}
}

CSS_FILE = "app.css"
THEME = './theme'