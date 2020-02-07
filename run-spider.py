from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from bankcrawler.spiders.links import LinksSpider

process = CrawlerProcess(get_project_settings())
process.crawl(LinksSpider)
process.start()