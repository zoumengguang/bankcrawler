import scrapy
import os
import csv
import re
from urllib.parse import urlparse

""" dataFile = os.environ['LOCAL_DATA_PATH'] """
dataFile = './data/productionBankList.csv'
bankFile = './data/bankSheet.csv'
visited = {}
dataDict = {}
bankSheetDict = {}
bankUrls = []
bankDomains = []

# Parse input .csv and populate dict/lists
reader = csv.DictReader(open(dataFile))
for row in reader:
    values = list(row.values())
    prodDomain = values[5].lower().replace(
        'http://', '').replace('https://', '').replace('/', '').replace('www.','')
    bankDomain = values[3].lower().replace(
        'http://', '').replace('https://', '').replace('/', '').replace('www.','')
    bankUrl = 'http://' + \
        values[5].lower() if not re.search('^https?://', values[5].lower()) else values[5].lower()
    dataDict[prodDomain] = {
        "Bank Name": values[1],
        'CCOS Link': values[5].rstrip('/')
    }
    bankUrls.append(bankUrl)
    bankDomains.append(prodDomain)
    bankDomains.append(bankDomain)
    # if values[4]: bankDomains.append(urlparse(values[4]).netloc)
    if values[5]: bankDomains.append(urlparse(values[5]).netloc)

#pp.pprint(dataDict)
#pp.pprint(bankUrls)
#pp.pprint(bankDomains)

reader2 = csv.DictReader(open(bankFile))
for row in reader2:
    values = list(row.values())
    bankSheetDict[values[1]] = {
        'agentId': values[0],
        'displayName': values[2],
        'storeName': values[3],
        'products': values[4],
        'city': values[6],
        'state': values[7],
        'zipcode': values[8],
        'agentWebsite': values[18],
        'productId1': values[19],
        'subproductId1': values[20],
        'productId2': values[21],
        'subproductId2': values[22],
        'productId3': values[23],
        'subproductId3': values[24],
    }

class LinksSpider(scrapy.Spider):
    name = 'spreadsheetFill'
    allowed_domains = bankDomains
    start_urls = bankUrls
    custom_settings = {'DEPTH_LIMIT': 3}

    def parse(self, response):
        curUrlStartDom = response.meta['start_url'].lower().replace(
            'http://', '').replace('https://', '').replace('/', '').replace('www.','')
        phoneNum = ''
        contactURL = ''
        email = ''
        emailre = '^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$'
        for href in response.xpath('//footer//@href').getall():
            if href.startswith('tel:'): phoneNum = href.replace('tel:','')
            if 'contact' in href.lower() and href.lower().startswith('http'): contactURL = href
            if href.startswith('mailto:') or re.search(emailre, href): email = href.replace('mailto:', '')
        address = response.xpath('//footer//address/text()').get()
        slug = curUrlStartDom.replace('.yourcommunitycard.com','')
        yield {
            'agentId': bankSheetDict[slug]['agentId'],
            'displayName': bankSheetDict[slug]['displayName'],
            'storeName': bankSheetDict[slug]['storeName'],
            'products': bankSheetDict[slug]['products'],
            'address': address,
            'city': bankSheetDict[slug]['city'],
            'state': bankSheetDict[slug]['state'],
            'zipcode': bankSheetDict[slug]['zipcode'],
            'supportPhone': phoneNum,
            'supportContactUs': contactURL,
            'contactFirstName': '',
            'contactLastName': '',
            'contactMiddleName': '',
            'contactEmailAddress': email,
            'Product Code (Classic)': '',
            'Product Code (Platinum)': '',
            'Product Code (Business)': '',
            'agentWebsite': bankSheetDict[slug]['agentWebsite'],
            'platinum pid': bankSheetDict[slug]['productId1'],
            'platinum subpid': bankSheetDict[slug]['subproductId1'],
            'platinum-rewards pid': bankSheetDict[slug]['productId2'],
            'platinum-rewards subpid': bankSheetDict[slug]['subproductId2'],
            'platinum-cash-rewards pid': bankSheetDict[slug]['productId3'],
            'platinum-cash-rewards subpid': bankSheetDict[slug]['subproductId3'],
        }