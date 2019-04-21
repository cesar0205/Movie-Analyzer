import requests

from time import sleep
from urllib.parse import quote_plus
from google_scraper.result_parser import Parser


class GoogleScraper():

    def __init__(self, query, country='mx', proxy=None,
                 results_per_page=50,
                 max_results=50, wait_time=30,
                 ignore_https_warnings=False,
                 start=0):

        # URL-encode query
        # self.query = quote_plus(query)
        self.query = query
        self.country = country;
        self.max_results = max_results
        self.wait_time = wait_time
        self.results_per_page = results_per_page
        self.start = start
        self.proxies = {}
        self.parser = Parser()
        self.response = None

        self.only_first_page = True;

        if (self.max_results < self.results_per_page):
            self.results_per_page = self.max_results;

        print("Results per page", self.results_per_page)
        print("Max results", self.max_results)

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip, deflate',
        }

        # Set default get request parameters.
        self.params = {
            'q': self.query,
            'start': self.start,
            'num': self.results_per_page,
            'gws_rd': 'cr',
            'gl': self.country,
        }

        # Supress https warnings
        if ignore_https_warnings:
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self.domain = 'google.com.mx'

    def crawl(self):
        """
        Crawl Google results pages, return parsed results.
        """
        results = []
        url = 'https://www.{}/search'.format(self.domain)
        while len(results) < self.max_results:
            response = requests.get(url,
                                    params=self.params,
                                    headers=self.headers,
                                    proxies=self.proxies,
                                    verify=False)
            response.raise_for_status()

            self.response = response;

            items = self.parser.parse_results(response.text)

            # Finish if there no results.
            if len(items) == 0:
                print('No results')
                break
            else:
                results += items

            # Finish if max results reached.
            # print("Checking length:", len(results), self.max_results)
            if len(results) >= self.max_results or self.only_first_page:
                print('Reached max results.')
                break

            # Get next page link
            next_page = self.parser.parse_next_page_link(response.text)
            # Finish if there no more pages of results.
            if not next_page:
                with open('debug.html', 'w') as f:
                    f.write(response.text)
                print('No more results to fetch.')
                break

            url = 'https://www.{}{}'.format(self.domain, next_page)
            # Remove start parameter - we have next page URL.
            try:
                del self.params['start']
            except KeyError:
                pass

            # Set referer as previous page, more human-like.
            self.headers['referer'] = response.url

            # Include a wait time if we are not finished collecting data.
            print('Wating 30 seconds before next request.')
            sleep(self.wait_time)

        # Trim to max result size
        results = results[:self.max_results]

        return results