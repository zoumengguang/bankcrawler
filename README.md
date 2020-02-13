# Bank Link Webcrawler

This is a web scraper containing various spiders written in Python using the Scrapy framework for purposes of crawling bank websites for information. Spiders take in a .csv file in various specified formats as an input, and outputs various results into the console or a .csv or .json format.

## Spiders
This spiders written for this project are the following:
### `links`
`links` is a webcrawler that simply scrapes the links from a list of designated websites, the links' response codes, their originating start URLs, and the name of the website itself.

### `linksExtract` (WIP)
`linksExtract` is a modified version of the `links` spider that contains additional Splash integration. The primary difference is the Splash middleware that fetches pages dependent on the use of JavaScript to get pages that Scrapy by itself would otherwise be unable to get.

## Usage
- Spiders run in a virtual environment on a Linux machine using `virtualenv`.
- From the virtual environment in the root of the project (e.g. `/bankcrawler` in this case)
you can run `scrapy crawl [SPIDER_NAME] -o [OUTPUT_FILE_NAME].[FILE_EXTENSION]`
- For example, to run `links`, do `scrapy crawl links` 
- If you wanted to output to a `.csv`, use the `-o` flag and do `scrapy crawl links -o links.csv`

For more detailed usage, please refer to the [Scrapy documentation](https://docs.scrapy.org/en/latest/index.html).

## Required Modules and Dependencies
- Python 3.6+
- Scrapy 1.8+
- Scrapy Splash 0.7.2+
- BeautifulSoup4 4.8.2+
