# generate other spiders
# cd ./src/
# scrapy genspider example example.com

from src.app import MyApp

if __name__ == '__main__':
    MyApp().run()