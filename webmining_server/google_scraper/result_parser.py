from bs4 import BeautifulSoup
from lxml import html as ht

class Parser():

    def parse_results(self, html):
        """
        Parse web search results.
        Ignore universal (news, image etc) results.
        """
        xpaths = [
            "//div[@class='rc']"
        ]

        data = []
        doc = ht.document_fromstring(html)

        for xpath in xpaths:
            results = doc.xpath(xpath)
            if len(results) > 0:
                break

        if not results:
            print("No results")
            return data


        for result in results:
            link = self.get_link(result)
            if len(link) > 0:
                # Ignore image links that are mixed in with standard results
                if not link.startswith('/images?q='):
                    data.append(link)
        return data

    def parse_next_page_link(self, html):
        """
        Parse next page link from html string.
        """
        doc = ht.document_fromstring(html)
        return self.get_next_page_link(doc)

    def get_next_page_link(self, html_tree):
        """
        Return next page link from results paginator.
        """
        try:
            return html_tree.xpath('//a[@id="pnnext"]/@href')[0]
        except IndexError:
            return None

    def get_link(self, html_tree):
        link = html_tree.xpath('div[@class="r"]/a/@href')[0]
        return link
