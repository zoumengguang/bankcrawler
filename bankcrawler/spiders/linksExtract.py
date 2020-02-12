# -*- coding: utf-8 -*-
# Spider takes input as .csv with env var to local file
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
visited = {}
bankDict = {}
bankUrls = []
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
        "Alpha Link": values[4].rstrip('/').replace('http://', '').replace('https://', ''),
        "Prod Link": values[5].rstrip('/').replace('http://', '').replace('https://', ''),
    }
    bankUrls.append(bankUrl)
    bankDomains.append(bankDomain)
    bankDomains.append(urlparse(values[4]).netloc)
    bankDomains.append(urlparse(values[5]).netloc)

class LinksSpider(scrapy.Spider):
    name = 'linksExtract'
    allowed_domains = bankDomains
    start_urls = bankUrls

    custom_settings = {
        'DEPTH_LIMIT': 3
    }

    # Override default start_requests func to force use of Splash
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='render.html', args={'wait': 0.5})

    def parse(self, response):
        """ # Get cur response start_url to access bankDict for comparing
        linkList = []
        for href in response.xpath('//a/@href').getall():
            if href.startswith('http'):
                linkList.append(href)
        pp.pprint(linkList) """
        curUrlDomain = response.meta['start_url'].lower().replace(
            'http://', '').replace('https://', '').replace('/', '').replace('www.','')
        # Use BeautifulSoup parser to get links from raw HTML returned from Scrapy Splash
        soup = BeautifulSoup(response.body)
        for link in soup.findAll('a', attrs={'href': re.compile("^https?://")}):
            href = link.get('href')
            curDomain = urlparse(href).netloc.replace('www.','')
            curPath = urlparse(href).path.rstrip('/')
            if not curPath:
                curPath = '/'
            if curDomain:
                if curDomain not in visited:
                    visited[curDomain] = set()
                if curPath not in visited[curDomain]:
                    visited[curDomain].add(curPath)
                    if bankDict[curUrlDomain]['Alpha Link'] in href:
                        yield {
                            'Bank Name': bankDict[curUrlDomain]['Bank Name'],
                            'Response Domain': urlparse(response.url).netloc,
                            'Response Path': urlparse(response.url).path,
                            'Link Type': bankDict[curUrlDomain]['Alpha Link']
                        }
                    elif bankDict[curUrlDomain]['Prod Link'] in href:
                        yield {
                            'Bank Name': bankDict[curUrlDomain]['Bank Name'],
                            'Response Domain': urlparse(response.url).netloc,
                            'Response Path': urlparse(response.url).path,
                            'Link Type': bankDict[curUrlDomain]['Prod Link']
                        }
            yield scrapy.Request(response.urljoin(href), self.parse)
