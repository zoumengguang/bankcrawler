# -*- coding: utf-8 -*-
import scrapy


class LinksSpider(scrapy.Spider):
    name = 'links'
    allowed_domains = ['unitedbanks.com']
    start_urls = ['http://unitedbanks.com/']

    def parse(self, response):
        pass
