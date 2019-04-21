# -*- coding: utf-8 -*-
import os
import sys
# Scrapy settings for scrapy_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'scrapy_spider'

SPIDER_MODULES = ['scrapy_spider.spiders']
NEWSPIDER_MODULE = 'scrapy_spider.spiders'

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

import sys
#sys.path.insert(0, '/Users/andrea/Desktop/book_packt/chapters/web mining/movie_reviews_analizer_app/webmining')
sys.path.insert(0, BASE_DIR+'/webmining_server')
# Setting up django's settings module name.
os.environ['DJANGO_SETTINGS_MODULE'] = 'webmining_server.settings'
#import django to load models(otherwise AppRegistryNotReady: Models aren't loaded yet):
import django
django.setup()



# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'scrapy_spider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 5000
CONCURRENT_REQUESTS_PER_DOMAIN = 3000
CONCURRENT_ITEMS = 200

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'scrapy_spider.pipelines.ReviewPipeline': 300,
}

LOG_ENABLED = True
LOG_LEVEL = 'INFO'
DEPTH_LIMIT = 2
