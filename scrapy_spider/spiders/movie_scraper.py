from newspaper import Article
from urllib.parse import urlparse
from scrapy.selector import Selector
from scrapy import Spider
from scrapy.spiders import BaseSpider, CrawlSpider, Rule
from scrapy.http import Request

from scrapy_spider import settings
from scrapy_spider.items import PageItem, SearchItem

unwanted_domains = ['youtube.com', 'www.youtube.com']
from nltk.corpus import stopwords

stopwords = set(stopwords.words('english'))

#scrapy crawl movie_spider -a url_list=https://www.allmovie.com/blog/post/the-martian-the-allmovie-review,https://www.metacritic.com/movie/the-martian -a search_key="mission mars"

#Remember the SearchTerm object with search_key term should exist in the database, otherwise we will get
#sentiment_analyzer.models.SearchTerm.DoesNotExist: SearchTerm matching query does not exist.

#Look for keywords in title + content
def check_query_in_review(keywords, title, content):
    #print(keywords)
    content_list = map(lambda x: x.lower(), content.split(' '))
    title_list = map(lambda x: x.lower(), title.split(' '))
    words = list(content_list) + list(title_list)
    #If any of the keywords is contained in the title + content word list then return True
    for k in keywords:
        if k in words:
            #print("Found some word in title content", k)
            return True
    return False

'''
    Scraper used to parse the content of the urls returned in the query search.
    The search depth is one as we are interesed only in parsing the content of the urls.
    The parsed pages will have a flag 'review' to indicate that this PageItem is a review.
'''
class Search(Spider):
    # Parameters set used for spider crawling
    name = 'movie_spider'

    #url_list: url list that the spider will srap.
    #search key:
    def __init__(self, url_list, search_key):  # specified by -a
        #print("base dir: ", settings.BASE_DIR)
        self.search_key = search_key
        self.keywords = [w.lower() for w in search_key.split(" ") if w not in stopwords]
        #print(url_list)
        self.start_urls = url_list.split(',')  # ['http://www.allmovie.com/blog/post/the-martian-the-allmovie-review']
        #print(len(self.start_urls))
        #print(self.start_urls)
        # allowed_domains = ['www.rottentomatoes.com','www.firstpost.com','www.theguardian.com','www.mirror.co.uk','www.comingsoon.net','www.independent.co.uk','www.newsok.com,'www.standard.co.uk','www.ew.com','www.heraldscotland.com','www.cnn.com','www.belfasttelegraph.co.uk','www.wsj.com','www.dailystar.co.uk','www.ibtimes.co.uk','www.denverpost.com','www.abcnews.go.com','www.radiotimes.com','www.latimes.com','www.telegraph.co.uk','artsbeat.blogs.nytimes.com','www.irishtimes.com','www.digitalspy.co.uk','www.digitaltrends.com','www.dailymail.co.uk','www.newsday.com','www.philadelphia.cbslocal.com','www.cbsnews.com','www.thewrap.com','www.rollingstone.com','www.movieweb.com','www.avclub.com','www.freebeacon.com','news.nationalpost.com','www.usatoday.com','www.deadline.com','www.nytimes.com','www.chicagotribune.com','www.amny.com','www.oregonlive.com','www.hollywoodreporter.com','www.celluloidcinema.com','hollywoodlife.com']

        super(Search, self).__init__(url_list)

    def start_requests(self):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        for url in self.start_urls:
            #print('request', url)
            yield Request(url=url, callback=self.parse_site, dont_filter=True, headers = headers)

    #Tries to parse the response object to an Acticle object.
    #If the title or the content were not successfully parsed, we will use a scrapy Selector to almost manually
    #extract these attributes.
    #We well create and save an PageItem object for each page that the spider collects, parses and most importantly,
    #contains the search_key term in its content/title.
    #Finally we link all PageItem objects with the SearchItem object specified by search_key term.
    #Returns a PageItem for each page that contains the search_key
    def parse_site(self, response):

        #print("Current depth: ", response.request.meta)
        #Exclude empty characters
        def crop_emptyel(arr):
            return [u for u in arr if u != ' ']

        domain = urlparse(response.url).hostname
        a = Article(response.url)
        a.download()
        a.parse()
        ## Get meta info from website

        title = a.title

        sel = Selector(response)
        if title == None:
            title = sel.xpath('//title/text()').extract()
            if len(title) > 0:
                title = title[0].strip().lower()

        content = a.text.replace('\n', '')

        #If we couldn't get the content using the newspaper library then we will try with Selector with several
        #filters
        if content == None:
            content = 'none'
            if len(crop_emptyel(sel.xpath('//div//article//p/text()').extract())) > 1:
                contents = crop_emptyel(sel.xpath('//div//article//p/text()').extract())
                #print('divarticle')
            elif len(crop_emptyel(sel.xpath('//article[contains(@class,"article")]//p/text()').extract())) > 1:
                #print('article')
                contents = crop_emptyel(sel.xpath('//article[contains(@class,"article")]//p/text()').extract())
            elif len(crop_emptyel(sel.xpath('//div[contains(@id,"content")]//p/text()').extract())) > 1:
                #print('using method 3')
                contents = crop_emptyel(sel.xpath('//div[contains(@id,"content")]//p/text()').extract())
            elif len(crop_emptyel(sel.xpath('//div[contains(@class,"body")]//p/text()').extract())) > 1:
                #print('using method 4')
                contents = crop_emptyel(sel.xpath('//div[contains(@class,"body")]//p/text()').extract())
            elif len(crop_emptyel(sel.xpath('//section[contains(@class,"text")]//p/text()').extract())) > 1:
                #print('using method 5')
                contents = crop_emptyel(sel.xpath('//section[contains(@class,"text")]//p/text()').extract())
            elif len(crop_emptyel(sel.xpath('//div[contains(@itemprop,"article")]//p/text()').extract())) > 0:
                #print('using method 6')
                contents = crop_emptyel(sel.xpath('//div[contains(@itemprop,"article")]//p/text()').extract())
            elif len(crop_emptyel(sel.xpath('//div//article[contains(@itemprop,"article")]//p/text()').extract())) > 1:
                #print('using method 7')
                contents = crop_emptyel(sel.xpath('//div//article[contains(@itemprop,"article")]//p/text()').extract())
            elif len(crop_emptyel(sel.xpath('//div[contains(@id,"description")]//span/text()').extract())) > 1:
                #print('using descr')
                contents = crop_emptyel(sel.xpath('//div[contains(@id,"description")]//span/text()').extract())
            elif len(crop_emptyel(sel.xpath('//div[contains(@class,"article")]//div/text()').extract())) > 1:
                #print('using div contains article');
                contents = crop_emptyel(sel.xpath('//div[contains(@class,"article")]//div/text()').extract())
            elif len(crop_emptyel(sel.xpath('//div[contains(@class,"article")]//p/text()').extract())) > 1:
                #print('using method 8')
                contents = crop_emptyel(sel.xpath('//div[contains(@class,"article")]//p/text()').extract())
            elif len(crop_emptyel(sel.xpath('//p[contains(@class,"lead")]//text()').extract())) > 0:
                #print('using method 9')
                contents = crop_emptyel(sel.xpath('//p[contains(@class,"lead")]//text()').extract())
            elif len(crop_emptyel(sel.xpath('//div[contains(@class,"text")]//p/text()').extract())) > 0:
                #print('using method 10')
                contents = crop_emptyel(sel.xpath('//div[contains(@class,"text")]//p/text()').extract())
            elif len(crop_emptyel(sel.xpath('/html/head/meta[@name="description"]/@content').extract())) > 0:
                contents = crop_emptyel(sel.xpath('/html/head/meta[@name="description"]/@content').extract())

            content = ' '.join([c for c in contents]).strip().lower()
        #print('title:', title)
        #print('content:',content)

        # get search item
        search_item = SearchItem.django_model.objects.get(term=self.search_key)
        # save item
        #If the PageItem object does not exist
        if not PageItem.django_model.objects.filter(url=response.url).exists():
            #check content and create PageItem if the content contains any of the keywords and the page domain is
            #allowed
            if len(content) > 0:
                if check_query_in_review(self.keywords, title, content):
                    if domain not in unwanted_domains:
                        newpage = PageItem()
                        newpage['searchterm'] = search_item
                        newpage['title'] = title
                        newpage['content'] = content
                        newpage['url'] = response.url
                        newpage['depth'] = 0
                        newpage['review'] = True
                        # newpage.save()
                        # The newpage object will be saved in the pipeline
                        return newpage
                else:
                    pass
                    #print("No keywords in title or content")
        else:
            return None
