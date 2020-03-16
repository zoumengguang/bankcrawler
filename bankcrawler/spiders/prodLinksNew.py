# -*- coding: utf-8 -*-
# Crawls bank websites to search for certain production and alpha links, and returns a boolean value for each on
# whether or not the link was found on the site.
# Spider takes input as .csv formatted in the exact way in specified in the file:
# ID Number | Bank Name | Address | Bank Website | Alpha Link | Production Link 
#
# TODO: Crawling only affects first page, see stackoverflow 
#
import scrapy
import os
import csv
import json
import re
import tldextract
from scrapy.http.headers import Headers
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from os.path import join, dirname
from dotenv import load_dotenv
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pprint

pp = pprint.PrettyPrinter(indent=3)

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

class ProdLinksSpider(CrawlSpider):
    name = 'prodLinksNew'
    custom_settings = {
        #'FEED_EXPORT_FIELDS': ["Bank Name", "Bank Domain", "Link Domain", "Link Path", "Link Type"]
        'FEED_FORMAT': 'csv',
        'FEED_URI': './csv/{}.csv'.format(name),
        'DEPTH_LIMIT': 10,
        #'LOG_ENABLED': False,
        #'LOG_LEVEL': 'INFO'
    }

    dataFile = os.environ['LOCAL_DATA_PATH']
    bankDict = {}
    bankUrls = []
    bankDomains = []
    blacklist = ['tel:', 'mailto:', '#', 'javascript:']

    # Parse .csv and populate dict/lists
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

    allowed_domains = bankDomains
    start_urls = bankUrls

    rules = [
        Rule(LinkExtractor(restrict_xpaths='//a/@href'), follow=True, callback='parse_item')
    ]

    # Override built-in start_requests to use Splash
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse_item, meta={
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
    def parse_item(self, response):
        # Get originating domain of current request
        curBankDomain = response.meta['start_url'].lower().replace(
            'http://', '').replace('https://', '').replace('/', '').replace('www.','')
        extracted = tldextract.extract(response.url.lower())
        curResponseDom = "{}.{}".format(extracted.domain, extracted.suffix)
        if (extracted.subdomain): curResponseDom = extracted.subdomain + '.' + curResponseDom
        curResponsePath = urlparse(response.url).path.rstrip('/')
        soup = BeautifulSoup(response.body, features='lxml')
        alpha_link = self.bankDict[curBankDomain]['Alpha Link']
        prod_link = self.bankDict[curBankDomain]['Prod Link']

        #print(curBankDomain)
        #print(curResponseDom)
        #print(curResponsePath)
        #print(self.bankDict[curBankDomain])

        # Edge case for certain sites putting links inside the onclick as a var to be passed in jQuery
        for link in soup.findAll('a', attrs={'onclick': re.compile("https?://")}):
            onclick = link.get('onclick').lower()
            if alpha_link in onclick:
                yield {
                    'Bank Name': self.bankDict[curBankDomain]['Bank Name'],
                    'Bank Domain': curBankDomain,
                    'Found Link Domain': curResponseDom,
                    'Found Link Path': curResponsePath,
                    'Link(Alpha/Prod)': self.bankDict[curBankDomain]['Alpha Link']
                }
            elif prod_link in onclick:
                yield {
                    'Bank Name': self.bankDict[curBankDomain]['Bank Name'],
                    'Bank Domain': curBankDomain,
                    'Found Link Domain': curResponseDom,
                    'Found Link Path': curResponsePath,
                    'Link(Alpha/Prod)': self.bankDict[curBankDomain]['Prod Link']
                }

        # Get all links in hrefs on page with HTTP/S
        # HTML response from Splash includes JS rendered content, whereas regular scrapy response does not
        for link in soup.findAll('a', attrs={'href': re.compile(".*")}):
            href = link.get('href').lower()
            if alpha_link in href:
                yield {
                    'Bank Name': self.bankDict[curBankDomain]['Bank Name'],
                    'Bank Domain': curBankDomain,
                    'Found Link Domain': curResponseDom,
                    'Found Link Path': curResponsePath,
                    'Link(Alpha/Prod)': self.bankDict[curBankDomain]['Alpha Link']
                }
            elif prod_link in href:
                yield {
                    'Bank Name': self.bankDict[curBankDomain]['Bank Name'],
                    'Bank Domain': curBankDomain,
                    'Found Link Domain': curResponseDom,
                    'Found Link Path': curResponsePath,
                    'Link(Alpha/Prod)': self.bankDict[curBankDomain]['Prod Link']
                }
            check = any(word in href for word in self.blacklist)
            print(href)
            if not check:
                yield scrapy.Request(response.urljoin(href), self.parse_item, meta={
                    'splash': {
                        'args': {
                            'timeout': 90, 
                            'wait': 0.5,
                            'resource_timeout': 60 
                        },
                        'endpoint': 'render.html'
                    }
                })

        # Scrapy response and splash response contain differing hrefs on the page? Must follow both
        # even if redundant
        for href in response.xpath('//a/@href').getall():
            print(href)
            check = any(word in href for word in self.blacklist)
            if not check:
                yield scrapy.Request(response.urljoin(href), self.parse_item, meta={
                    'splash': {
                        'args': {
                            'timeout': 90, 
                            'wait': 0.5,
                            'resource_timeout': 60 
                        },
                        'endpoint': 'render.html'
                    }
                })
