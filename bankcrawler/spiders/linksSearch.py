import scrapy
import os
import csv
import re
from urllib.parse import urlparse
from scrapy_splash import SplashRequest
from bs4 import BeautifulSoup
import pprint

pp = pprint.PrettyPrinter(indent=3)

""" dataFile = os.environ['LOCAL_DATA_PATH'] """
dataFile = './data/productionBankList.csv'
targetLinks = './data/targetLinks.csv'
# Track visited paths to avoid repetitive crawling, domain: set() of paths mapping
visited = {}
# Parsed CSV information
bankDict = {}
targetDict = {}
# Start URLs
bankUrls = []
# Allowed Domains
bankDomains = []

# Parse input .csv and populate dict/lists
reader = csv.DictReader(open(dataFile))
for row in reader:
    values = list(row.values())
    bankDomain = values[3].lower().replace(
        'http://', '').replace('https://', '').replace('/', '').replace('www.','')
    bankUrl = 'http://' + \
        values[3].lower() if not re.search('^https?://', values[3].lower()) else values[3].lower()
    bankDict[bankDomain] = {
        "Bank Name": values[1],
        "Bank URL": bankUrl.rstrip('/'),
    }
    bankUrls.append(bankUrl)
    bankDomains.append(bankDomain)
    # if values[4]: bankDomains.append(urlparse(values[4]).netloc)
    # if values[5]: bankDomains.append(urlparse(values[5]).netloc)

# 2nd file parser for list of target links to search for
reader2 = csv.DictReader(open(targetLinks))
for row in reader2:
    values = list(row.values())
    linkDomain = urlparse(values[0]).netloc.lower().replace('http://', '').replace('https://', '').replace(
        'www.','').rstrip('/')
    bankDomains.append(linkDomain)
    targetDict[linkDomain] = {
        "Description": values[1]
    }

#pp.pprint(bankDict)
#pp.pprint(targetDict)
#pp.pprint(bankUrls)
#pp.pprint(bankDomains)

class LinksSpider(scrapy.Spider):
    name = 'linksSearch'
    allowed_domains = bankDomains
    start_urls = bankUrls
    custom_settings = {'DEPTH_LIMIT': 3}

    # Override default start_requests func to force use of Splash w/ each request
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='render.html', args={'wait': 0.5})

    # Todo: Output is incorrectly putting blank path
    # parse receives response obj containing both raw HTML from Splash and regular response content
    # loops through both response.body with raw HTML and response itself using xpath to access elements
    def parse(self, response):
        curUrlStartDom = response.meta['start_url'].lower().replace(
            'http://', '').replace('https://', '').replace('/', '').replace('www.','')
        soup = BeautifulSoup(response.body, features='lxml')
        curResponseDom = urlparse(response.url).netloc
        curResponsePath = urlparse(response.url).path
        # Search HTML response body from JS content with Splash + parse with BeautifulSoup
        for link in soup.findAll('a', attrs={'href': re.compile("^https?://")}):
            href = link.get('href')
            curDomain = urlparse(href).netloc.replace('www.','')
            curPath = urlparse(href).path.rstrip('/')
            if curDomain:
                if curDomain not in visited:
                    visited[curDomain] = set()
                if curPath not in visited[curDomain]:
                    visited[curDomain].add(curPath)
                    if curDomain in targetDict:
                        yield {
                            'Bank Name': bankDict[curUrlStartDom]['Bank Name'],
                            'Response Domain': curResponseDom,
                            'Response Path': curResponsePath,
                            'Found Link': curDomain,
                            'Description': targetDict[curDomain]['Description']
                        }
        
        # Search response directly with xpath
        # Only create new requests from xpath vars b/c Splash raw HTML doesn't
        # get all the hrefs on site (unknown reason)
        for href in response.xpath('//a/@href').getall():
            if href.startswith('http'):
                curDomain = urlparse(href).netloc.replace('www.','')
                curPath = urlparse(href).path.rstrip('/')
                if curDomain:
                    if curDomain not in visited:
                        visited[curDomain] = set()
                    if curPath not in visited[curDomain]:
                        visited[curDomain].add(curPath)
                        if curDomain in targetDict:
                            yield {
                                'Bank Name': bankDict[curUrlStartDom]['Bank Name'],
                                'Response Domain': curResponseDom,
                                'Response Path': curResponsePath,
                                'Found Link': curDomain,
                                'Description': targetDict[curDomain]['Description']
                            }
            yield scrapy.Request(response.urljoin(href), self.parse)
