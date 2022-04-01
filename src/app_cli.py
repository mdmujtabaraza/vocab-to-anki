from multiprocessing import Process, Queue
# from queue import Queue
# from threading import Thread
import webbrowser
import validators
import time
from datetime import datetime as dt
import requests
import json
import re
# import sys
# if 'twisted.internet.reactor' in sys.modules:
# 	del sys.modules['twisted.internet.reactor']

import urllib3
from gtts import gTTS
from twisted.internet import reactor
from scrapy import crawler
import scrapy
from scrapy import signals
from scrapy.http.request import Request
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

from src.dict_scraper.items import CambridgeDictionaryItem
from src.dict_scraper.spiders.cambridge import CambridgeSpider, MeaningsSpider
from src.lib.json_to_apkg import JsonToApkg


# 'SPIDER_MIDDLEWARES': {
# 'scrapy.contrib.spidermiddleware.referer.RefererMiddleware': True,
# },

SPIDER_SETTINGS = {
    'ROBOTSTXT_OBEY': True,
    'DEFAULT_REQUEST_HEADERS': {
        'Referer': 'https://www.google.com'
    },
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
        'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
    },
    'FAKEUSERAGENT_PROVIDERS': [
        'scrapy_fake_useragent.providers.FakeUserAgentProvider',  # this is the first provider we'll try
        # if FakeUserAgentProvider fails, we'll use faker to generate a user-agent string for us
        'scrapy_fake_useragent.providers.FakerProvider',
        'scrapy_fake_useragent.providers.FixedUserAgentProvider',  # fall back to USER_AGENT value
    ],
    'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    # 'ITEM_PIPELINES': {'__main__.MeaningsPipeline': 1}
}
CONTAINER = {'url': '', 'dictionary': [], 'meanings': []}


# class MeaningsPipeline(object):
#     def process_item(self, item, spider):
#         CONTAINER['meanings'].append(item)

# CrawlerProcess  works only single time
# class UrlCrawlerScript(Process):
#     def __init__(self, spider, q, *args):
#         Process.__init__(self)
#         # settings = get_project_settings()
#         self.crawler = CrawlerProcess(SPIDER_SETTINGS)
#         # self.crawler.configure()
#         self.spider = spider
#         self.q = q
#         self.args = args
#
#     def run(self):
#         self.crawler.crawl(self.spider, self.q, self.args)
#         self.crawler.start()
#         reactor.run()

# def run_spider(spider, *args):
#     q = Queue()
#     crawler = UrlCrawlerScript(spider, q, *args)
#     crawler.start()
#     if spider is MeaningsSpider:
#         CONTAINER['meanings'] = q.get()[0]
#     else:  # spider is CambridgeSpider:
#         CONTAINER['dictionary'] = q.get()[0]
#     crawler.join()

# CrawlerRunner with multiprocessing.Process and multiprocessing.Queue  works
# class UrlCrawlerScript(Process):
#     def __init__(self, spider, q, *args):
#         Process.__init__(self)
#         self.runner = CrawlerRunner(get_project_settings())
#         self.spider = spider
#         self.q = q
#         self.args = args
#         self.d = None
#
#     def run(self):
#         deferred = self.runner.crawl(self.spider, self.q, self.args)
#         deferred.addBoth(lambda _: reactor.stop())
#         reactor.run()
#
#
# def run_spider(spider, *args):
#     q = Queue()
#     crawler = UrlCrawlerScript(spider, q, *args)
#     crawler.start()
#     print(q.get()[0])
#     # if spider is MeaningsSpider:
#     #     CONTAINER['meanings'] = q.get()[0]
#     # else:  # spider is CambridgeSpider:
#     #     CONTAINER['dictionary'] = q.get()[0]
#     crawler.join()


# CrawlerRunner with threading.Thread and queue.Queue  not works
# class UrlCrawlerScript(Thread):
#     def __init__(self, spider, q, *args):
#         Thread.__init__(self)
#         self.runner = CrawlerRunner(get_project_settings())
#         self.spider = spider
#         self.q = q
#         self.args = args
#         self.d = None
#
#     def run(self):
#         deferred = self.runner.crawl(self.spider, self.q, self.args)
#         deferred.addBoth(lambda _: reactor.stop())
#         reactor.run()
#
#
# def run_spider(spider, *args):
#     q = Queue()
#     runner = UrlCrawlerScript(spider, q, *args)
#     runner.start()
#     print(q.get()[0])
#     # if spider is MeaningsSpider:
#     #     CONTAINER['meanings'] = q.get()[0]
#     # else:  # spider is CambridgeSpider:
#     #     CONTAINER['dictionary'] = q.get()[0]
#     runner.join()

# defered join and defered reactor stop in main
# def run_spider(spider, *args):
#     q = Queue()
#     runner = CrawlerRunner(get_project_settings())
#     runner.crawl(spider, q, args)
#     if not reactor.running:
#         Thread(target=reactor.run).start()
#     print(q.get()[0])
#     # if spider is MeaningsSpider:
#     #     CONTAINER['meanings'] = q.get()[0]
#     # else:  # spider is CambridgeSpider:
#     #     CONTAINER['dictionary'] = q.get()[0]


# One more way, use CrawlerRunner in main
# def run_spider(runner, spider, *args):
#     q = Queue()
#     runner.crawl(spider, q, args)
#     # if not reactor.running:
#     #     Thread(target=reactor.run).start()
#     print(q.get()[0])
#     # if spider is MeaningsSpider:
#     #     CONTAINER['meanings'] = q.get()[0]
#     # else:  # spider is CambridgeSpider:
#     #     CONTAINER['dictionary'] = q.get()[0]

class CrawlerRunnerProcess(Process):
    def __init__(self, spider, q, *args):
        Process.__init__(self)
        self.runner = CrawlerRunner(get_project_settings())
        self.spider = spider
        self.q = q
        self.args = args
        self.d = None

    def run(self):
        deferred = self.runner.crawl(self.spider, self.q, self.args)
        deferred.addBoth(lambda _: reactor.stop())
        reactor.run(installSignalHandlers=False)


def run_spider(spider, *args):
    q = Queue()
    runner = CrawlerRunnerProcess(spider, q, *args)
    runner.start()
    # print(q.get()[0])
    # if spider is MeaningsSpider:
    #     CONTAINER['meanings'] = q.get()[0]
    # else:  # spider is CambridgeSpider:
    #     CONTAINER['dictionary'] = q.get()[0]
    runner.join()
    return q.get()

# # the wrapper to make it run more times
# def run_spider(spider, *args):
#     def f(q):
#         try:
#             runner = crawler.CrawlerRunner()
#             deferred = runner.crawl(spider, *args)
#             deferred.addBoth(lambda _: reactor.stop())
#             reactor.run()
#             q.put(None)
#         except Exception as e:
#             q.put(e)
#
#     q = Queue()
#     p = Process(target=f, args=(q,))
#     p.start()
#     result = q.get()
#     p.join()
#
#     if result is not None:
#         raise result


configure_logging()

if __name__ == '__main__':
    # word_url = "https://dictionary.cambridge.org/dictionary/english/stand"
    # gcurl = "https://webcache.googleusercontent.com/search?q=cache:" + word_url
    # runner = CrawlerRunner(SPIDER_SETTINGS)
    # runner.crawl(MeaningsSpider, ((gcurl),))
    # runner.crawl(MeaningsSpider, ((gcurl),))
    # # runner.crawl(CambridgeSpider, gcurl,
    # #              "com", dt.now().strftime("%Y%m%d%H%M%S"))
    # d = runner.join()
    # d.addBoth(lambda _: reactor.stop())
    # reactor.run()  # the script will block here until all crawling jobs are finished
    # print(CONTAINER['meanings'])
    pass
