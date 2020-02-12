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
dataFile = './data/banklist1.csv'
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
    bankDomain = values[0].replace(
        'http://', '').replace('https://', '').replace('/', '')
    bankUrl = 'http://' + \
        values[0] if not re.search('^https?://', values[0]) else values[0]
    bankDict[bankDomain] = {
        "Bank Name": values[4],
        "Bank URL": bankUrl.rstrip('/'),
        "Alpha Link": values[2].rstrip('/').replace('http://', '').replace('https://', ''),
        "Prod Link": values[3].rstrip('/').replace('http://', '').replace('https://', ''),
    }
    bankUrls.append(bankUrl)
    bankDomains.append(bankDomain)

pp = pprint.PrettyPrinter(indent=3)
#pp.pprint(bankDict)

class ProdLinksSpider(scrapy.Spider):
    name = 'prodLinks1'
    # allowed_domains = bankDomains
    start_urls = bankUrls
    custom_settings = {
        'DEPTH_LIMIT': 2,
        'FEED_EXPORT_FIELDS': ["Bank Name", "Bank Domain", "Link Domain", "Link Path", "Link Type"]
    }

    # print(response.request) Response type (GET, POST) and url
    # print(response.status) HTTP status code
    # print(response.request.meta.get('redirect_urls')) get all followed redirect urls to get to current path
    # print(response.meta['start_url']) custom middleware to get originating start_url of current url
    def parse(self, response):
        # Get originating domain of current request
        curUrlDomain = response.meta['start_url'].replace(
            'http://', '').replace('https://', '').replace('/', '')
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
                        print(hrefTrim)
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
