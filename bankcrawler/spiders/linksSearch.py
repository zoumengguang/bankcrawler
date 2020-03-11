import scrapy
import os
import csv
import re
import tldextract
from os.path import join, dirname
from dotenv import load_dotenv
from urllib.parse import urlparse
from scrapy_splash import SplashRequest
from bs4 import BeautifulSoup
import pprint

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

pp = pprint.PrettyPrinter(indent=3)

class LinksSpider(scrapy.Spider):
    name = 'linksSearch'
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': './csv/{}.csv'.format(name),
        'FEED_EXPORT_ENCODING': 'utf-8',
        'DEPTH_LIMIT': 3,
        'LOG_ENABLED': True,
        'LOG_LEVEL': 'INFO'
    }

    # List of banks
    dataFile = os.environ['LOCAL_DATA_PATH']
    # List of target links to search for
    targetLinks = os.environ['LOCAL_SHEET_PATH']

    # Track visited paths to avoid repetitive crawling, domain: set() of paths mapping
    #visitedSplash = {}
    #visited = {}
    # Avoid repeated output due to double scanning of webpages
    output = {}
    # Parsed CSV information
    bankDict = {}
    targetDict = {}
    # Start URLs for Scrapy
    bankUrls = []
    # Allowed Domains to traverse
    bankDomains = []

    # Parse input .csv and populate dict/lists
    reader = csv.DictReader(open(dataFile))
    for row in reader:
        values = list(row.values())
        bankDomain = values[5].lower().replace(
            'http://', '').replace('https://', '').replace('/', '').replace('www.','')
        bankUrl = 'http://' + \
            values[5].lower() if not re.search('^https?://', values[5].lower()) else values[5].lower()
        bankDict[bankDomain] = {
            "Bank Name": values[0],
        }
        if bankUrl: bankUrls.append(bankUrl)
        if bankDomain: bankDomains.append(bankDomain)

    # 2nd file parser for list of target links to search for
    reader2 = csv.DictReader(open(targetLinks))
    for row in reader2:
        values = list(row.values())
        extracted = tldextract.extract(values[0])
        linkDomain = "{}.{}".format(extracted.domain, extracted.suffix)
        if (linkDomain and linkDomain not in bankDomains): bankDomains.append(linkDomain)
        if (extracted.subdomain): linkDomain = extracted.subdomain + '.' + linkDomain
        targetDict[linkDomain] = {
            "Description": values[1]
        }

    allowed_domains = bankDomains
    start_urls = bankUrls

    #pp.pprint(bankDict)
    #pp.pprint(targetDict)
    #pp.pprint(bankUrls)
    #pp.pprint(bankDomains)

    # Override default start_requests func to force use of Splash w/ each request
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, 
                args={
                    'timeout': 90, 
                    'wait': 0.5,
                    'resource_timeout': 45 
                },
                endpoint='render.html'
            )

    """
    Parse method scans the site's response twice, once with Scrapy's response object and another using
    Splash's returned HTML response containing content retrievable only through JS.
    Ignores non-link hrefs and uses the 'visited' set obj to track traversed domain/path combos
    """
    def parse(self, response):
        curUrlStartDom = response.meta['start_url'].lower().replace(
            'http://', '').replace('https://', '').replace('/', '').replace('www.','')
        soup = BeautifulSoup(response.body, features='lxml')
        extracted = tldextract.extract(response.url.lower())
        curResponseDom = "{}.{}".format(extracted.domain, extracted.suffix)
        if (extracted.subdomain): curResponseDom = extracted.subdomain + '.' + curResponseDom
        curResponsePath = urlparse(response.url).path.rstrip('/')
        # Search HTML response body from JS content with Splash + parse with BeautifulSoup
        for link in soup.findAll('a', attrs={'href': re.compile("^https?://")}):
            href = link.get('href').lower()
            for target in self.targetDict.keys():
                if target in href:
                    yield {
                        'Bank Name': self.bankDict[curUrlStartDom]['Bank Name'],
                        'Response Domain': curResponseDom.replace('www.',''),
                        'Response Path': curResponsePath,
                        'Found Link': href,
                        'Description': self.targetDict[target]['Description']
                    }
                    
                #curPath = urlparse(href).path.lower().rstrip('/')
                """ if curDomain not in visitedSplash:
                    visitedSplash[curDomain] = set()
                if curPath not in visitedSplash[curDomain]:
                    visitedSplash[curDomain].add(curPath) """
                # Check if link on page is in list of targets
                """ # Check output dict to see if it was yielded already
                if curResponseDom + curResponsePath not in output:
                    output[curResponseDom + curResponsePath] = set()
                if href not in output[curResponseDom + curResponsePath]:
                    output[curResponseDom + curResponsePath].add(href)
                    yield {
                        'Bank Name': bankDict[curUrlStartDom]['Bank Name'],
                        'Response Domain': curResponseDom,
                        'Response Path': curResponsePath,
                        'Found Link': href,
                        'Description': targetDict[curDomain]['Description']
                    } """

            yield scrapy.Request(response.urljoin(href), self.parse, meta={
                'splash': {
                    'args': {
                        'timeout': 90, 
                        'wait': 0.5,
                        'resource_timeout': 45 
                    },
                    'endpoint': 'render.html'
                }
            })
                               
        
        # Search response directly with xpath
        # Only create new requests from xpath vars b/c Splash raw HTML doesn't
        # get all the hrefs on site (unknown reason)
        """ for href in response.xpath('//a/@href').getall():
            href = href.lower()
            if href.startswith('http') and not href.endswith(('.pdf','.jpg','.png','.gif','aspx')):
                extracted = tldextract(href)
                curDomain = "{}.{}".format(extracted.domain, extracted.suffix)
                if (extracted.subdomain): curDomain = extracted.subdomain + '.' + curDomain
                #curPath = urlparse(href).path.rstrip('/')
                if curDomain:
                    if curDomain not in visited:
                        visited[curDomain] = set()
                    if curPath not in visited[curDomain]:
                        visited[curDomain].add(curPath)
                    for target in targetDict.keys():
                        if target in href:
                            yield {
                                'Bank Name': bankDict[curUrlStartDom]['Bank Name'],
                                'Response Domain': curResponseDom,
                                'Response Path': curResponsePath,
                                'Found Link': href,
                                'Description': targetDict[curDomain]['Description']
                            }
                            # Check output dict to see if it was yielded already
                            if curResponseDom + curResponsePath not in output:
                                output[curResponseDom + curResponsePath] = set()
                            if href not in output[curResponseDom + curResponsePath]:
                                output[curResponseDom + curResponsePath].add(href)
                                yield {
                                    'Bank Name': bankDict[curUrlStartDom]['Bank Name'],
                                    'Response Domain': curResponseDom,
                                    'Response Path': curResponsePath,
                                    'Found Link': href,
                                    'Description': targetDict[curDomain]['Description']
                                } 
            if not href.endswith('.aspx'):
                yield SplashRequest(response.urljoin(href), self.parse, endpoint='render.html', 
                    args={
                        'timeout': 90, 
                        'wait': 5,
                        'resource_timeout': 30 
                    }) """
