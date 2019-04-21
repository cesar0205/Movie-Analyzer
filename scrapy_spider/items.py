# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


from scrapy_djangoitem import DjangoItem
from sentiment_analyzer.models import Page,Link,SearchTerm

class SearchItem(DjangoItem):
    django_model = SearchTerm
class PageItem(DjangoItem):
    django_model = Page
class LinkItem(DjangoItem):
    django_model = Link
