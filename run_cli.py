import os
os.environ['UA_PLATFORM'] = "android"
import requests
import urllib3
import urllib
from urllib.request import Request, urlopen
import requests_random_user_agent

from src.app_cli import run_spider
from src.dict_scraper.spiders import cambridge


if __name__ == '__main__':
    word_url = "https://dictionary.cambridge.org/dictionary/english/sit"
    word_url2 = "https://dictionary.cambridge.org/dictionary/english/run"
    gcurl = "https://webcache.googleusercontent.com/search?q=cache:" + word_url
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'Referer': 'https://www.google.com'
    }
    # # response = requests.get(gcurl, headers=headers)
    # # print(response.content)
    # CONTAINER['url'] = gcurl

    http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=1.0, read=2.0))
    response = http.request('GET', word_url, headers=headers, retries=urllib3.Retry(5, redirect=2))
    print(response.status)
    # print(response.data)
    # print(response["headers"])

    # req = Request(word_url)
    # req.add_header('User-Agent', 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)')
    # content = urlopen(req).read()
    # print(content)

    # print(urllib.request.urlopen(word_url))

    # s = requests.Session()
    # s.headers.update({'Referer': 'https://www.google.com'})
    # print(s.headers['User-Agent'], s.headers['Referer'])
    #
    # # Without a session
    # resp = requests.get('https://httpbin.org/user-agent')
    # print(resp.json()['user-agent'])

    # 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) '
    # 'Chrome/85.0.4183.140 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'

    # print(run_spider(cambridge.MeaningsSpider, word_url, headers))
    # time.sleep(20)
    # print(run_spider(cambridge.MeaningsSpider, word_url2, headers))

    # run_spider(CambridgeSpider, gcurl, "com", "cbed-2-4", False)  # dt.now().strftime("%Y%m%d%H%M%S")
    # run_spider("https://dictionary.cambridge.org/dictionary/english/water", "com", dt.now().strftime("%Y%m%d%H%M%S"))
