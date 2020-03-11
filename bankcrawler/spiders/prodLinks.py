# -*- coding: utf-8 -*-
# Crawls bank websites to search for certain production and alpha links, and returns a boolean value for each on
# whether or not the link was found on the site.
# Spider takes input as .csv formatted in the exact way in specified in the file:
# ID Number | Bank Name | Address | Bank Website | Alpha Link | Production Link 

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

pp = pprint.PrettyPrinter(indent=3)

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

#dataFile = os.environ['LOCAL_DATA_PATH']
dataFile = './data/productionBankList.csv'
visited = {}
bankDict = {}
bankUrls = []
bankDomains = []

# Parse .csv and populate dict/lists
# visited - Dictionary of set objects with domain: path entries 
#   for tracking visited paths on a specified domain
# Bank Dict - Main information store for each bank
# Bank Urls - List of starting URLs for spider to crawl
# Bank Domains - List of allowed domains spider can visit
reader = csv.DictReader(open(dataFile))
for row in reader:
    values = list(row.values())
    bankDomain = values[3].lower().replace(
        'http://', '').replace('https://', '').replace('/', '').replace('www.','')
    bankUrl = 'http://' + \
        values[3].lower() if not re.search('^https?://', values[3].lower()) else values[3].lower()
    alphaLink = values[4].lower().replace(
        'http://', '').replace('https://', '').replace('/', '').replace('www.','')
    prodLink = values[5].lower().replace(
        'http://', '').replace('https://', '').replace('/', '').replace('www.','')
    bankDict[bankDomain] = {
        "Bank Name": values[1],
        "Bank URL": bankUrl.rstrip('/'),
        "Alpha Link": alphaLink,
        "Prod Link": prodLink,
    }
    if bankUrl: bankUrls.append(bankUrl)
    if bankDomain: bankDomains.append(bankDomain)
    bankDomains.append(alphaLink)
    bankDomains.append(prodLink)

#pp.pprint(bankDict)
#pp.pprint(bankUrls)
#pp.pprint(bankDomains)

class ProdLinksSpider(scrapy.Spider):
    name = 'prodLinks'
    allowed_domains = bankDomains
    start_urls = bankUrls
    custom_settings = {
        #'FEED_EXPORT_FIELDS': ["Bank Name", "Bank Domain", "Link Domain", "Link Path", "Link Type"]
        'FEED_FORMAT': 'csv',
        'FEED_URI': './csv/{}.csv'.format(name),
        'FEED_EXPORT_ENCODING': 'utf-8',
        'DEPTH_LIMIT': 3,
        'LOG_ENABLED': False,
        'LOG_LEVEL': 'INFO'
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse, meta={
                'splash': {
                    'args': {
                        'timeout': 90, 
                        'wait': 0.5,
                        'resource_timeout': 60 
                    },
                    'endpoint': 'render.html'
                }
            })

    # print(response.request) Response type (GET, POST) and url
    # print(response.status) HTTP status code
    # print(response.request.meta.get('redirect_urls')) get all followed redirect urls to get to current path
    # print(response.meta['start_url']) custom middleware to get originating start_url of current url
    def parse(self, response):
        # Get originating domain of current request
        curBankDomain = response.meta['start_url'].lower().replace(
            'http://', '').replace('https://', '').replace('/', '').replace('www.','')
        extracted = tldextract.extract(response.url.lower())
        curResponseDom = "{}.{}".format(extracted.domain, extracted.suffix)
        if (extracted.subdomain): curResponseDom = extracted.subdomain + '.' + curResponseDom
        curResponsePath = urlparse(response.url).path.rstrip('/')
        soup = BeautifulSoup(response.body, features='lxml')

        # Get all links on page with HTTP/S
        for link in soup.findAll('a', attrs={'href': re.compile("^https?://")}):
            href = link.get('href').lower()
            """ if curDomain not in visited:
                visited[curDomain] = set()
            if curPath not in visited[curDomain]:
                visited[curDomain].add(curPath)"""

            if bankDict[curBankDomain]['Alpha Link'] in href:
                yield {
                    'Bank Name': bankDict[curBankDomain]['Bank Name'],
                    'Bank Domain': curBankDomain,
                    'Found Link Domain': curResponseDom,
                    'Found Link Path': curResponsePath,
                    'Link(Alpha/Prod)': bankDict[curBankDomain]['Alpha Link']
                }
            elif bankDict[curBankDomain]['Prod Link'] in href:
                yield {
                    'Bank Name': bankDict[curBankDomain]['Bank Name'],
                    'Bank Domain': curBankDomain,
                    'Found Link Domain': curResponseDom,
                    'Found Link Path': curResponsePath,
                    'Link(Alpha/Prod)': bankDict[curBankDomain]['Prod Link']
                }

        for href in response.xpath('//a/@href').getall():
            yield scrapy.Request(response.urljoin(href), self.parse, meta={
                'splash': {
                    'args': {
                        'timeout': 90, 
                        'wait': 0.5,
                        'resource_timeout': 60 
                    },
                    'endpoint': 'render.html'
                }
            })
