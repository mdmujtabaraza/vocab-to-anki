# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class DictScraperItem(Item):
    # define the fields for your item here like:
    # name = Field()
    pass


class CambridgeDictionaryItem(Item):
    word = Field()
    word_type = Field()
    meaning = Field()
    example_sentences = Field()
    phonemic_script = Field()
    pronunciation_word = Field()
    # pronunciation_meaning = Field()
    # pronunciation_sentence = Field()
    # guide_word = Field()
    synonyms = Field()

    # TODO: add other fields
    # or phonemic_scripts = {'us': '', 'uk': ''}
    # or pronunciations = {'us': '', 'uk': ''}
    # image = Field()

    # TODO: what if there are other types of the same word for ex: noun, verb, adverb...


class MeaningsItem(Item):
    meanings = Field()
    # meanings = [
    #     {'word': word, 'pos': part_of_speech, 'gw': guide_word},
    #     .
    #     .
    # ]
