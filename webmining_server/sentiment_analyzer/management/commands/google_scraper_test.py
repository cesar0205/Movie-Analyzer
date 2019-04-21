from google_scraper.google_scraper import GoogleScraper

from django.core.management.base import BaseCommand, CommandError

#python manage.py google_scraper_test --query="the martian movie"

class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--query', dest='query',
                             type=str, action='store',
                             help='Query to perform on Google');



    def handle(self, *args, **options):
         query = str(options['query'])
         spider = GoogleScraper(query)
         results = spider.crawl()
         print(results)



