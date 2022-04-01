# generate other spiders
# cd ./src/
# scrapy genspider example example.com
# pip list --format=freeze > requirements.txt
from os import environ
if 'ANDROID_STORAGE' in environ:
    environ['UA_PLATFORM'] = "android"

from src.app import MyApp

if __name__ == '__main__':
    MyApp().run()
