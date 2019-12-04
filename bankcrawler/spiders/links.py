# -*- coding: utf-8 -*-
import scrapy
from urlparse import urlparse

# set to track visited domains
url_set = set()

class LinksSpider(scrapy.Spider):
    name = 'links'
    allowed_domains = ['unitedbank.com']
    start_urls = ['http://www.unitedbank.com']

    def parse(self, response):
        for href in response.xpath('//a/@href').getall():
            if href.startswith('http') and 'unitedbank.com' not in href:
                domain = urlparse(href).netloc
                if domain and domain not in url_set:
                    url_set.add(domain)
                    yield { 'url': domain }
            yield scrapy.Request(response.urljoin(href), self.parse)
