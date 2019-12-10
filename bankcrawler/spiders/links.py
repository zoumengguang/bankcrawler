# -*- coding: utf-8 -*-
# Spider takes input as .csv with env var to local file
import scrapy
import os
import csv
import re
""" import pprint """
from urlparse import urlparse

LOCAL_DATA_PATH = os.getenv('LOCAL_DATA_PATH')
visited = {}
bankDict = {}
bankUrls = []
bankDomains = []

""" pp = pprint.PrettyPrinter(indent=4) """

# Parse .csv and populate dict/lists
reader = csv.DictReader(open(LOCAL_DATA_PATH))
for row in reader:
    values = row.values()
    bankDomain = values[0].replace(
        'http://', '').replace('https://', '').replace('/', '')
    bankUrl = 'http://' + \
        values[0] if not re.search('^https?://', values[0]) else values[0]
    bankDict[bankDomain] = {
        "FDIC Cert": values[3],
        "Bank URL": bankUrl,
        "IDRSSD": values[1],
        "Bank Name": values[2],
        "ABA Routing Number": values[4],
    }
    bankUrls.append(bankUrl)
    bankDomains.append(bankDomain)

class LinksSpider(scrapy.Spider):
    name = 'links'
    """ allowed_domains = ['unitedbank.com']
    start_urls = ['http://www.unitedbank.com'] """
    allowed_domains = bankDomains
    start_urls = bankUrls

    # handle_httpstatus_list = [400, 404, 500]

    # print(response.request) Response type (GET, POST) and url
    # print(response.status) HTTP status code
    # print(response.request.meta.get('redirect_urls')) get all followed redirect urls to get to current path
    # print(response.meta['start_url']) get originating start_url of current url
    def parse(self, response):
        for href in response.xpath('//a/@href').getall():
            if href.startswith('http'):
                curDomain = urlparse(href).netloc
                curPath = urlparse(href).path
                if curDomain:
                    if curDomain not in visited.keys(): 
                        visited[curDomain] = set()
                    if curPath not in visited[curDomain]:
                        curUrlOrgStart = response.meta['start_url'].replace(
                            'http://', '').replace('https://', '').replace('/', '')
                        curBankID = bankDict[curUrlOrgStart]['FDIC Cert']
                        linkType = 'Internal' if curDomain in curUrlOrgStart else 'External'
                        visited[curDomain].add(curPath)
                        yield {
                            'FDIC Cert': curBankID,
                            'Bank Domain': curUrlOrgStart,
                            'Link Type': linkType,
                            'Link Domain': curDomain,
                            'Link Path': curPath,
                            'Link Status Response': response.status
                        }
            yield scrapy.Request(response.urljoin(href), self.parse)
