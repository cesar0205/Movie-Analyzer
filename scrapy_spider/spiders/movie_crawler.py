# from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request

from scrapy_spider.items import PageItem, LinkItem, SearchItem

'''
    Crawler that collects and travels through links that will be used by the page rank algorithm.
    This is the most commonly used spider for crawling regular websites, as it provides a convenient 
    mechanism for following links by defining a set of rules.
    When visiting a web page for a review we will extract the title, content, source_url, current_url, depth
'''
class Search(CrawlSpider):
    # Parameters set used for spider crawling
    name = 'movie_crawl_spider'

    #url_list, A url list with the start urls to visit;
    #search_id, Id of the SearchItem to look for

    def __init__(self, url_list, search_id):  # specified by -a

        self.start_urls = url_list.split(',')
        self.search_id = int(search_id)

        print("Start urls")
        print(self.start_urls)
        print("Search id", self.search_id)

        # allow any link but
        #'fontSize=*', 'infoid=*', 'SortBy=*' : These terms indicate that the link refers to the same page but with
        # different view properties. That's why we don't want to process it.
        self.rules = (
            Rule(LinkExtractor(allow=(), deny=('fontSize=*', 'infoid=*', 'SortBy=*',), unique=True),
                 callback='parse_item', follow=True),
        )
        super(Search, self).__init__(url_list)



    def parse_item(self, response):
        sel = Selector(response)
        print("Current depth: ", response.request.meta['depth'])

        ## Get meta info from website
        title = sel.xpath('//title/text()').extract()
        if len(title) > 0:
            title = title[0]

        ##We are not that interested in the content, that's why we don't apply more filters to force having
        ##something in the content field.
        #We are more interested in the depth, fromulr and tourl that we will use for our page rank algorith.
        contents = sel.xpath('/html/head/meta[@name="description"]/@content').extract()
        content = ' '.join([c for c in contents]).strip()

        #Get source url

        fromurl = response.request.headers['Referer'].decode('ascii', 'ignore');

        #Get current url
        tourl = response.url
        #Get depth
        depth = response.request.meta['depth']

        # Get search item using its id.
        search_item = SearchItem.django_model.objects.get(id=self.search_id)

        # If a PageItem linked to the current url does not exist, then create a new one.
        if not PageItem.django_model.objects.filter(url=tourl).exists():
            newpage = PageItem()
            newpage['searchterm'] = search_item
            newpage['title'] = title
            newpage['content'] = content
            newpage['url'] = tourl
            newpage['depth'] = depth
            newpage.save()  # cant use pipeline cause the execution can finish here
        '''
        print("============================================")
        try:
            print("--From url", fromurl)
            print('--title:', title)
            print('--depth: ', depth)
        except ValueError:
            print("##########################################  Encoding error")
            print(fromurl.encode("ascii", "ignore"))
            print(title.encode("ascii", "ignore"))
            raise
        '''
        # print contents
        # if( int(depth)> 1):
        #   print fromurl,'--title:',title,'-',response.url,' depth:',depth

        # Get source PageItem, and current PageItem and get their ids

        from_page = PageItem.django_model.objects.get(url=fromurl)
        from_id = from_page.id
        to_page = PageItem.django_model.objects.get(url=tourl)
        to_id = to_page.id

        #Create a link from the previous page to the current page.
        # If a LinkItem linking source link and current link doesn't exist we will create a new one-
        if not LinkItem.django_model.objects.filter(from_id=from_id).filter(to_id=to_id).exists():
            newlink = LinkItem()
            newlink['searchterm'] = search_item
            newlink['from_id'] = from_id
            newlink['to_id'] = to_id
            newlink.save()
