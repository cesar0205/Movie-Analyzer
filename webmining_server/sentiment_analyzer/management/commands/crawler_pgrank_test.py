from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option
from sentiment_analyzer.models import Page,SearchTerm
import os

#python manage.py crawler_pgrank_test --search_term=matt damon the martian

class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--search_term', dest='search_term',
                             type=str, action='store',
                             help='Id of the search term to delete');

        parser.add_argument('--num_reviews', dest='num_reviews',
                             type=int, action='store',
                             help='Number of reviews to start crawling');


    def handle(self, *args, **options):
         search_term = str(options['search_term'])
         num_reviews = options['num_reviews']
         if num_reviews == None:
            #default
            num_reviews = 5
         #print num_reviews
         print("Term to start searching ", search_term, num_reviews)
         s = SearchTerm.objects.get(term=search_term)
         search_id = s.id

         print("Id of the search term", s.id)
         pages = s.pages.all().filter(review=True)
         urls = []
         for u in pages:
             print("Start page ", u.id)
             urls.append(u.url)
         #crawl
         #print settings.BASE_DIR
         print("Command to throw")
         cmd = 'cd '+settings.BASE_DIR+'../../scrapy_spider & scrapy crawl movie_crawl_spider -a url_list=%s -a search_id=%s' %('\"'+str(','.join(urls[:num_reviews]))+'\"','\"'+str(search_id)+'\"')
         print('cmd:',cmd)
         os.system(cmd)