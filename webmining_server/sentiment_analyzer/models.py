from django.db import models

class SearchTerm(models.Model):
    term = models.CharField(max_length=255)
    num_reviews = models.IntegerField(null=True, default=0)

    # display term on admin panel
    def __str__(self):
        return self.term


class Page(models.Model):
    searchterm = models.ForeignKey(SearchTerm, related_name='pages', on_delete=models.SET_NULL, null=True, blank=True)
    url = models.URLField(default='', blank=True)
    title = models.CharField(max_length=255)
    depth = models.IntegerField(null=True, default=-1)
    html = models.TextField(blank=True, default='')
    review = models.BooleanField(default=False)
    rank = models.FloatField(null=True, default=1)
    content = models.TextField(blank=True, default='')
    sentiment = models.IntegerField(null=True, default=100)


class Link(models.Model):
    searchterm = models.ForeignKey(SearchTerm, related_name='links', on_delete=models.SET_NULL, null=True, blank=True)
    from_id = models.IntegerField(null=True)
    to_id = models.IntegerField(null=True)
