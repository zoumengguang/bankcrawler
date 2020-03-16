# -*- coding: utf-8 -*-
# Scrapy settings for bankcrawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#from shutil import which
import os
from os.path import join, dirname
from dotenv import load_dotenv

BOT_NAME = 'bankcrawler'

SPIDER_MODULES = ['bankcrawler.spiders']
NEWSPIDER_MODULE = 'bankcrawler.spiders'

# Load env vars from .env file using dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'bankcrawler (+' + os.getenv('AGENT_DOMAIN') + ')'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 96

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 5
DOWNLOAD_TIMEOUT = 180
RANDOMIZE_DOWNLOAD_DELAY = True
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 6
# CONCURRENT_REQUESTS_PER_IP = 32

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    'bankcrawler.middlewares.StartRequestsMiddleware': 543, 
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
#    'scrapy_selenium.SeleniumMiddleware': 800
#    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
#    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'bankcrawler.pipelines.BankcrawlerPipeline': 300,
#}

# Number of times to retry a request
RETRY_TIMES = 1

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 1
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 0.25
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 128
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = True

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Domain Depth Settings
#DEPTH_LIMIT = 1

# Output Settings
#FEED_FORMAT = 'csv'
#FEED_URI = 'linksOut.csv'
#LOG_LEVEL = 'INFO'
#LOG_FILE = 'links.log'

# Scrapy Splash Settings
# !!!!!!!!!!!!!!!!!!!!!!----IMPORTANT----!!!!!!!!!!!!!!!!!!!!!
# Set SPLASH_URL to 'splash' when using composing docker image, use 'localhost' for testing
#SPLASH_URL = 'http://splash:8050/'
#SPLASH_URL = 'http://{}:8050/'.format(os.environ['SPLASH_IP'])
SPLASH_URL = 'http://localhost:8050/'
SPLASH_COOKIES_DEBUG = True
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# Scrapy Selenium Settings
#SELENIUM_DRIVER_NAME = 'firefox'
#SELENIUM_DRIVER_EXECUTABLE_PATH = which('geckodriver')
#SELENIUM_DRIVER_ARGUMENTS=['-headless']  # '--headless' if using chrome instead of firefox

# Error code handling since Scrapy does not allow error codes 300+
# HTTPERROR_ALLOWED_CODES = [400, 404, 500]

# Logging settings for terminal, makes running spiders faster when False
#LOG_ENABLED = False
