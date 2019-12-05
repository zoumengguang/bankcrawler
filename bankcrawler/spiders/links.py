# -*- encoding: utf-8 -*-
# Spider takes input as .csv with env var to local file
import scrapy, os, csv
""" import pprint """
from urlparse import urlparse
from bankcrawler.items import BankcrawlerItem

LOCAL_DATA_PATH = os.getenv('LOCAL_DATA_PATH')
bankDict = {}
bankUrls = []
bankDomains = []

""" pp = pprint.PrettyPrinter(indent=4) """

# Parse .csv and populate dict/lists
reader = csv.DictReader(open(LOCAL_DATA_PATH))
for row in reader:
    values = row.values()
    bankDict[int(values[3])] = { "Bank Domain": values[0], "IDRSSD": values[1], "Bank Name": values[2], "ABA Routing Number": values[4] }
    bankUrls.append(values[0])
    bankDomains.append(values[0].replace('http://','').replace('https://','').replace('/',''))
    """ pp.pprint(bankDict[int(values[3])]) """

""" print(bankUrls)
print(bankDomains) """

url_set = set()

class LinksSpider(scrapy.Spider):
    name = 'links'
    allowed_domains = ['unitedbank.com']
    start_urls = ['http://www.unitedbank.com']
    """     allowed_domains = bankDomains
    start_urls = bankUrls """

    def parse(self, response):
        # print(response.request) Response type and url
        # print(response.status) HTTP status code
        # print(response.request.meta.get('redirect_urls')) get all followed redirect urls to get to current path
        print(response.meta['start_url'])
        for href in response.xpath('//a/@href').getall():
            """ item = BankcrawlerItem() """
            """ if href.startswith('http'): """
            if href.startswith('http') and 'unitedbank.com' not in href:
                domain = urlparse(href).netloc
                """ item["domain"] = urlparse(href).netloc
                item["path"] = urlparse(href).path """
                if domain and domain not in url_set:
                    url_set.add(domain)
                    yield { "url": domain }
            yield scrapy.Request(response.urljoin(href), self.parse)
