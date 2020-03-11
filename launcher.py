import sys
import csv

from bankcrawler.crawl import crawl

def scrape(event={}, context={}):
    crawl(**event)

if __name__ == "__main__":
    try:
        event = csv.DictReader(open(sys.argv[1]))
    except IndexError:
        event = {}
    scrape(event)