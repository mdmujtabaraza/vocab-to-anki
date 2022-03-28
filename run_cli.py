from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor

from src.app_cli import run_spider
from src.dict_scraper.spiders.cambridge import MeaningsSpider
from scrapy.utils.log import configure_logging


if __name__ == '__main__':
    configure_logging()
    word_url = "https://dictionary.cambridge.org/dictionary/english/stand"
    gcurl = "https://webcache.googleusercontent.com/search?q=cache:" + word_url
    # # response = requests.get(gcurl, headers=headers)
    # # print(response.content)
    # CONTAINER['url'] = gcurl
    run_spider(MeaningsSpider, word_url)
    # run_spider(CambridgeSpider, gcurl, "com", "cbed-2-4", False)  # dt.now().strftime("%Y%m%d%H%M%S")
    # run_spider("https://dictionary.cambridge.org/dictionary/english/water", "com", dt.now().strftime("%Y%m%d%H%M%S"))
