from sentiment_analyzer.models import Link,Page,SearchTerm
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

# python manage.py delete_query --search_term_id=x

class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--search_term_id', dest='search_term_id',
                             type=int, action='store',
                             help='Id of the search term to delete');

    def handle(self, *args, **options):
         searchid = options['search_term_id']
         if searchid == None:
             print("The search id is empty:")
             #list
             for sobj in SearchTerm.objects.all():
                 print('id:',sobj.id,"  term:",sobj.term)
         else:
             print('delete...')
             search_obj = SearchTerm.objects.get(id=searchid)
             pages = search_obj.pages.all()
             pages.delete()
             links = search_obj.links.all()
             links.delete()
             search_obj.delete()
