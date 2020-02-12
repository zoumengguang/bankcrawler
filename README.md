### Bank Link Webcrawler

This is a web scraper written in Python using the Scrapy Web Crawler Framework that takes in a .csv file in various specified formats, and outputs a list of categorized links of the sites traversed.

This spiders written for this project are the following:
# links.py
links.py is a webcrawler that simply scrapes the links from a list of designated websites, and either logs them out to the console or into a .csv file.

# linksExtract.py (WIP)
linksExtract.py is a modified version of links.py that contains additional Scrapy Splash integration. The primary difference is the Splash middleware that fetches pages dependent on the use of JavaScript to get pages that Scrapy by itself would otherwise be unable to get.
