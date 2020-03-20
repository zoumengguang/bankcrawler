# -*- coding: utf-8 -*-
# Spider takes input as .csv with env var to local file
import scrapy
import os
import csv
import re
from os.path import join, dirname
from dotenv import load_dotenv
from urllib.parse import urlparse
from scrapy_splash import SplashRequest
from bs4 import BeautifulSoup

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

class LinksSpider(scrapy.Spider):
    name = 'linksExtract'
    custom_settings = {
        #'LOG_FILE': './logs/linksExtract.log',
        #'LOG_LEVEL': 'DEBUG',
        #'FEED_FORMAT': 'csv',
        #'FEED_URI': './csv/linksExtract.csv',
        'DEPTH_LIMIT': 4
    }

    dataFile = os.environ['LOCAL_DATA_PATH']
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
    
    allowed_domains = bankDomains
    start_urls = bankUrls

    allowed_domains = bankDomains
    start_urls = bankUrls

    # Override default start_requests func to force use of Splash w/ each request
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='render.html', args={'wait': 0.5})

    # parse receives response obj containing both raw HTML from Splash and regular response content
    # loops through both response.body with raw HTML and response itself using xpath to access elements
    # Treat each invocation of parse as a singular page with links returned as a response obj
    def parse(self, response):
        curUrlStartDom = response.meta['start_url'].lower().replace(
            'http://', '').replace('https://', '').replace('/', '').replace('www.','')
        soup = BeautifulSoup(response.body, features='lxml')
        curResponseDom = urlparse(response.url).netloc
        curResponsePath = urlparse(response.url).path
        # Search HTML response body from JS content with Splash + parse with BeautifulSoup
        for link in soup.find_all('a', attrs={'href': re.compile("^https?://")}):
            href = link.get('href')
            curDomain = urlparse(href).netloc.replace('www.','')
            curPath = urlparse(href).path.rstrip('/')
            if curDomain:
                if curDomain not in self.visited:
                    self.visited[curDomain] = set()
                if curPath not in self.visited[curDomain]:
                    self.visited[curDomain].add(curPath)
                    if self.bankDict[curUrlStartDom]['Alpha Link'] in href:
                        yield {
                            'Bank Name': self.bankDict[curUrlStartDom]['Bank Name'],
                            'Response Domain': curResponseDom,
                            'Response Path': curResponsePath,
                            'Link Type': 'Alpha Link',
                            'Prod/Alpha Link': self.bankDict[curUrlStartDom]['Alpha Link']
                        }
                    elif self.bankDict[curUrlStartDom]['Prod Link'] in href:
                        yield {
                            'Bank Name': self.bankDict[curUrlStartDom]['Bank Name'],
                            'Response Domain': curResponseDom,
                            'Response Path': curResponsePath,
                            'Link Type': 'Production Link',
                            'Prod/Alpha Link': self.bankDict[curUrlStartDom]['Prod Link']
                        }
        # Search response directly with xpath
        # Only create new requests from xpath vars b/c Splash raw HTML doesn't
        # get all the hrefs on site (unknown reason)
        for href in response.xpath('//a/@href').getall():
            if href.startswith('http'):
                curDomain = urlparse(href).netloc.replace('www.','')
                curPath = urlparse(href).path.rstrip('/')
                if curDomain:
                    if curDomain not in self.visited:
                        self.visited[curDomain] = set()
                    if curPath not in self.visited[curDomain]:
                        self.visited[curDomain].add(curPath)
                        if self.bankDict[curUrlStartDom]['Alpha Link'] in href:
                            yield {
                                'Bank Name': self.bankDict[curUrlStartDom]['Bank Name'],
                                'Response Domain': curResponseDom,
                                'Response Path': curResponsePath,
                                'Link Type': 'Alpha Link',
                                'Prod/Alpha Link': self.bankDict[curUrlStartDom]['Alpha Link']
                            }
                        elif self.bankDict[curUrlStartDom]['Prod Link'] in href:
                            yield {
                                'Bank Name': self.bankDict[curUrlStartDom]['Bank Name'],
                                'Response Domain': curResponseDom,
                                'Response Path': curResponsePath,
                                'Link Type': 'Production Link',
                                'Prod/Alpha Link': self.bankDict[curUrlStartDom]['Prod Link']
                            }
            yield scrapy.Request(response.urljoin(href), self.parse)
