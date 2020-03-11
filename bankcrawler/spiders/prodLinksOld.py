# -*- coding: utf-8 -*-
# Crawls bank websites to search for certain production and alpha links, and returns a boolean value for each on
# whether or not the link was found on the site.
# Spider takes input as .csv formatted in the exact way in specified in the file:
# ID Number | Bank Name | Address | Bank Website | Alpha Link | Production Link 

import scrapy
import os
import csv
import re
from urllib.parse import urlparse
import pprint

""" dataFile = os.environ['LOCAL_DATA_PATH'] """
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
    bankDict[bankDomain] = {
        "Bank Name": values[1],
        "Bank URL": bankUrl.rstrip('/'),
        "Alpha Link": values[4].lower().rstrip('/').replace('http://', '').replace('https://', ''),
        "Prod Link": values[5].lower().rstrip('/').replace('http://', '').replace('https://', ''),
    }
    if bankUrl: bankUrls.append(bankUrl)
    if bankDomain: bankDomains.append(bankDomain)

pp = pprint.PrettyPrinter(indent=3)

class ProdLinksSpider(scrapy.Spider):
    name = 'prodLinksOld'
    # allowed_domains = bankDomains
    start_urls = bankUrls
    custom_settings = {
        'FEED_EXPORT_FIELDS': ["Bank Name", "Bank Domain", "Link Domain", "Link Path", "Link Type"],
        'DEPTH_LIMIT': 3
    }

    # print(response.request) Response type (GET, POST) and url
    # print(response.status) HTTP status code
    # print(response.request.meta.get('redirect_urls')) get all followed redirect urls to get to current path
    # print(response.meta['start_url']) custom middleware to get originating start_url of current url
    def parse(self, response):
        # Get originating domain of current request
        curUrlDomain = response.meta['start_url'].replace(
            'http://', '').replace('https://', '').replace('/', '').replace('www.','')
        # Get all links on page with HTTP/S
        for href in response.xpath('//a/@href').getall():
            if href.startswith('http'):
                hrefTrim = href.rstrip('/')
                curHrefDomain = urlparse(hrefTrim).netloc
                curPath = urlparse(hrefTrim).path
                if curHrefDomain:
                    if curHrefDomain not in visited:
                        visited[curHrefDomain] = set()
                    if curPath not in visited[curHrefDomain]:
                        visited[curHrefDomain].add(curPath)                       
                        if bankDict[curUrlDomain]['Alpha Link'] in href:
                            yield {
                                'Bank Name': bankDict[curUrlDomain]['Bank Name'],
                                'Bank Domain': curUrlDomain,
                                'Link Domain': curHrefDomain,
                                'Link Path': curPath,
                                'Link Type': 'Alpha'
                            }
                        elif bankDict[curUrlDomain]['Prod Link'] in href:
                            yield {
                                'Bank Name': bankDict[curUrlDomain]['Bank Name'],
                                'Bank Domain': curUrlDomain,
                                'Link Domain': curHrefDomain,
                                'Link Path': curPath,
                                'Link Type': 'Production'
                            }
            yield scrapy.Request(response.urljoin(href), self.parse)