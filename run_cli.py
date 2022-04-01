import time

from src.app_cli import run_spider
from src.dict_scraper.spiders import cambridge


if __name__ == '__main__':
    word_url = "https://dictionary.cambridge.org/dictionary/english/stand"
    word_url2 = "https://dictionary.cambridge.org/dictionary/english/run"
    gcurl = "https://webcache.googleusercontent.com/search?q=cache:" + word_url
    # # response = requests.get(gcurl, headers=headers)
    # # print(response.content)
    # CONTAINER['url'] = gcurl

    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'Referer': 'https://www.google.com'
    }

    print(run_spider(cambridge.MeaningsSpider, word_url, headers))
    time.sleep(20)
    print(run_spider(cambridge.MeaningsSpider, word_url2, headers))

    # run_spider(CambridgeSpider, gcurl, "com", "cbed-2-4", False)  # dt.now().strftime("%Y%m%d%H%M%S")
    # run_spider("https://dictionary.cambridge.org/dictionary/english/water", "com", dt.now().strftime("%Y%m%d%H%M%S"))
