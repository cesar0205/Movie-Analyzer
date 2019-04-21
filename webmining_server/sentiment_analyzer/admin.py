from django.contrib import admin

# Register your models here.
from sentiment_analyzer.models import SearchTerm, Page, Link


class SearchTermAdmin(admin.ModelAdmin):
    list_display = ['id', 'term', 'num_reviews']
    ordering = ['-id']

class PageAdmin(admin.ModelAdmin):
    list_display = ['id', 'searchterm', 'url', 'title','content']
    ordering = ['-id', '-rank']

admin.site.register(SearchTerm, SearchTermAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Link)