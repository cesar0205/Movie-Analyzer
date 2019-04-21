from django.shortcuts import render
import datetime
import os
#import urllib2
import urllib
import numpy
import json
from django.shortcuts import render
from django.core.cache import cache
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template import loader
from django.core.cache import cache
from sentiment_analyzer.models import Page,SearchTerm
from pgrank.pgrank import pg_rank
import nltk.classify.util, nltk.metrics

from nltk.corpus import movie_reviews
from nltk.corpus import stopwords
from google_scraper.google_scraper import GoogleScraper

import collections
import logging

#PARAMETERS
test_mode = False
#Number of reviews to analyse
num_reviews = 20
num_bestwords = 20000
stopwords = set(stopwords.words('english'))
method_selfeatures = 'best_words_features'

# Create your views here.

#Extract the url keys from each review in the test file.
def parse_test_results():
    file_data = open(os.path.dirname(__file__)+'/bing_the_martian_results.json','r')
    bing_json = json.load(file_data)
    #print(len(bing_json['d']['results']))
    reviews_urls = [ d['Url'] for d in bing_json['d']['results']]
    #print(reviews_urls)
    return reviews_urls

def analyzer(request):
    context = {}

    print("Getting cache...", cache.get('test_data'))

    if request.method == 'POST':
        #The form sends data through a post request. We need to take the data and transform it into a query form
        print("============Entering to POST analyser function")
        post_data = request.POST
        query = post_data.get('query', None)
        print("Entering to post ", query)
        if query:
            return redirect('%s?%s' % (reverse('analyzer'),
                                       urllib.parse.urlencode({'q': query})))
    elif request.method == 'GET':
        print("===========Entering to GET anayser function")
        get_data = request.GET
        query = get_data.get('q')
        print("query..", query)
        if not query:
            return render(request, 'movie_reviews/home.html', context)

        context['query'] = query
        stripped_query = query.strip().lower()
        urls = []

        if test_mode:
            #Use test results from a scraping query.
            print("In test mode... parsing test results")
            stripped_query = "matt damon the martian"
            urls = parse_test_results()
        else:
            print("Trying google scraper")
            spider = GoogleScraper(stripped_query)
            urls = spider.crawl()
            print("urls, ", urls)

        if len(urls) == 0:
            return render(request, 'movie_reviews/noreviewsfound.html', context)

        print('=============urls:', str(urls[:num_reviews]))
        #Check if the query exists
        if not SearchTerm.objects.filter(term=stripped_query).exists():
            #Create SearchTerm because the spider will use it to link each Page to it.
            print("SearchTerm does not exist... creating one...with stripped", stripped_query)
            s = SearchTerm(term=stripped_query)
            s.save()
            try:
                # scrape
                print("Current directory..", os.getcwd())
                print("*******************************")
                cmd = 'cd ../scrapy_spider & scrapy crawl movie_spider -a url_list=%s -a search_key=%s' % (
                '\"' + str(','.join(urls[:num_reviews]).encode('utf-8')) + '\"', '\"' + str(stripped_query) + '\"')
                print('cmd:', cmd)
                os.system(cmd)
            except:
                print('error!')
                s.delete()
        else:
            # collect the pages already scraped
            print("Search term does exist, getting object")
            s = SearchTerm.objects.get(term=stripped_query)

        # calc num pages
        pages = s.pages.all().filter(review=True)
        if len(pages) == 0:
            s.delete()
            return render(request, 'movie_reviews/noreviewsfound.html', context)

        s.num_reviews = len(pages)
        s.save()

        context['searchterm_id'] = int(s.id)


        clf = cache.get('clf')
        best_sentiment_words = cache.get('best_sentiment_words')
        print("******************************=====================")
        print(best_sentiment_words)
        print(cache.get('test_data'))

        # Filter words that are the best words in the nltk movie_reviews corpus.
        # The best words are chosen according to the chi square score between words and their sentiment correlation.
        def best_words_features(words):
            return dict([(word, True) for word in words if word in best_sentiment_words])

        if clf == None:
            print("Classifier not set on cache...")

        cntpos = 0
        cntneg = 0
        for p in pages:
            words = p.content.split(" ")
            feats = best_words_features(words)  # bigram_word_features(words)#stopword_filtered_word_feats(words)
            # print feats
            pred_sent = clf.classify(feats)
            if pred_sent == 'pos':
                p.sentiment = 1
                cntpos += 1
            else:
                p.sentiment = -1
                cntneg += 1
            p.save()

        context['reviews_classified'] = len(pages)
        context['positive_count'] = cntpos
        context['negative_count'] = cntneg
        context['classified_information'] = True

        print("El contexto es:::::::::::::::", context['searchterm_id'])
    return render(request, 'movie_reviews/home.html', context)


def pgrank_view(request, pk):
    context = {}
    get_data = request.GET
    scrape = get_data.get('scrape', 'False')
    s = SearchTerm.objects.get(id=pk)

    if scrape == 'True':
        pages = s.pages.all().filter(review=True)
        urls = []
        for u in pages:
            urls.append(u.url)
        # crawl
        cmd = 'cd ../scrapy_spider & scrapy crawl movie_crawl_spider -a url_list=%s -a search_id=%s' % (
        '\"' + str(','.join(urls[:]).encode('utf-8')) + '\"', '\"' + str(pk) + '\"')
        print('cmd:', cmd)
        os.system(cmd)

    links = s.links.all()
    if len(links) == 0:
        context['no_links'] = True
        return render_to_response(
            'movie_reviews/pg-rank.html', RequestContext(request, context))

    # calc pgranks
    pg_rank(pk)
    # load pgranks in descending order of pagerank
    pages_ordered = s.pages.all().filter(review=True).order_by('-rank')
    context['pages'] = pages_ordered

    return render(request, 'movie_reviews/pg-rank.html', context)

def about(request):
    return render(request, 'movie_reviews/about.html',
                          {})