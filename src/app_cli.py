from src.dict_scraper.spiders import cambridge
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


def run_spider(soup_spider, url, headers, *args, **kwargs):
    spider = soup_spider(url, headers, *args, **kwargs)
    results = spider.parse()
    if spider is cambridge.MeaningsSpider:
        CONTAINER['meanings'] = results
    else:  # spider is CambridgeSpider:
        CONTAINER['dictionary'] = results
    print("CONTAINER:", CONTAINER)
    return results


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
