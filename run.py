# generate other spiders
# cd ./src/
# scrapy genspider example example.com
# pip list --format=freeze > requirements.txt

from twisted.internet import reactor

from src.app import crawler_runner, MyApp

if __name__ == '__main__':
    MyApp().run()
    deferred = crawler_runner.join()
    deferred.addBoth(lambda _: reactor.stop())
