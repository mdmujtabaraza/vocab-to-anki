from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
import time

from src.app_cli import run_spider
from src.dict_scraper.spiders.cambridge import MeaningsSpider
from scrapy.utils.log import configure_logging


if __name__ == '__main__':
    configure_logging()
    word_url = "https://dictionary.cambridge.org/dictionary/english/stand"
    word_url2 = "https://dictionary.cambridge.org/dictionary/english/run"
    gcurl = "https://webcache.googleusercontent.com/search?q=cache:" + word_url
    # # response = requests.get(gcurl, headers=headers)
    # # print(response.content)
    # CONTAINER['url'] = gcurl

    runner = CrawlerRunner(get_project_settings())
    run_spider(runner, MeaningsSpider, word_url)
    time.sleep(5)
    run_spider(runner, MeaningsSpider, word_url2)
    deferred = runner.join()
    deferred.addBoth(lambda _: reactor.stop())

    # run_spider(CambridgeSpider, gcurl, "com", "cbed-2-4", False)  # dt.now().strftime("%Y%m%d%H%M%S")
    # run_spider("https://dictionary.cambridge.org/dictionary/english/water", "com", dt.now().strftime("%Y%m%d%H%M%S"))
