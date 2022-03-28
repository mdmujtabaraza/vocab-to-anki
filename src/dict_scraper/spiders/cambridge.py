import re
import sys
import shutil

from scrapy import Spider, signals
from scrapy.http.request import Request
from twisted.internet import reactor
from gtts import gTTS
from scrapy import Selector
from scrapy.utils.response import open_in_browser

from src.dict_scraper.items import CambridgeDictionaryItem, MeaningsItem
from src.lib.json_to_apkg import JsonToApkg


# class CambridgeSpider(Spider):
#     name = 'cambridge'
#
#     def __init__(self, word, *args, **kwargs):
#         super(CambridgeSpider, self).__init__(*args, **kwargs)
#         self.word = word
#
#     def start_requests(self):
#         # with open('urls.txt', 'rb') as urls:
#         #     for url in urls:
#         yield Request('https://dictionary.cambridge.org/dictionary/english/' + getattr(self, 'word'),
#                       self.parse)
#
#     allowed_domains = ['dictionary.cambridge.org']
#     # start_urls = [
#     #     # 'https://dictionary.cambridge.org/dictionary/english/' + self.word,
#     # ]
#
#     def parse(self, response):
#         dictionary_item = CambridgeDictionaryItem()
#
#         # word = response.css("#cald4-1+ .dpos-h .hw").css("::text").extract_first()
#         word = response.css(".hw.dhw").css("::text").extract_first()
#         # word_type = response.css("#cald4-1+ .dpos-h .dpos").css("::text").extract_first()
#         word_type = response.css(".dpos").css("::text").extract_first()
#         meaning = response.css(".db").css("::text").extract()
#         example_sentences = response.css(".dexamp").css("::text").extract()
#         # todo: add different accents
#         phonemic_script = response.css(".uk .lpl-1").css("::text").extract_first()  # todo: what if 2 audio
#         # us_phonemic_script = response.css(".us .lpl-1").css("::text").extract_first()
#         pronunciation_word = response.css(".uk #ampaudio1 source::attr(src)").extract_first()  # amp-audio
#         # us_pronunciation = response.css(".us #ampaudio2 source::attr(src)").extract_first()  # amp-audio
#
#         def download_audio(accent: str, address: str) -> str:
#             filename = word + '_' + accent + '.mp3'
#
#             tts = gTTS(word, lang='en', tld='co.uk')
#             tts.save(filename)
#
#             # url = 'https://' + CambridgeSpider.allowed_domains[0] + address
#             # http = urllib3.PoolManager(10, headers={'user-agent': USER_AGENT})
#             # # r1 = http.urlopen('GET', 'http://httpbin.org/headers')
#             # # print(r1.data)
#             #
#             # # 1
#             # r = http.request('GET', url, preload_content=False)
#             # with open(filename, 'wb') as out:
#             #     while True:
#             #         data = r.read(2**16)  # 65536
#             #         if not data:
#             #             break
#             #         out.write(data)
#             # r.release_conn()
#
#             # 2
#             # with http.request('GET', url, preload_content=False) as resp, open(filename, 'wb') as out_file:
#             #     shutil.copyfileobj(resp, out_file)
#             # resp.release_conn()
#
#             # 3
#             # with open(filename, 'wb') as out:
#             #     r = http.request('GET', url, preload_content=False)
#             #     shutil.copyfileobj(r, out)
#
#             # 4
#             # with http.request('GET', url, preload_content=False) as r, open(filename, 'wb') as out_file:
#             #     shutil.copyfileobj(r, out_file)
#
#             return '[sound:' + filename + ']'
#
#         dictionary_item['word'] = word
#         dictionary_item['word_type'] = word_type
#         dictionary_item['meaning'] = ''.join(meaning).split(':')[0]  # todo: extract different sentences based on type
#         # dictionary_item['example_sentences'] = ''.join(example_sentences).split('.')[:2]
#         dictionary_item['example_sentences'] = re.findall('.*?[.!?]', ''.join(example_sentences))[:2]
#         dictionary_item['phonemic_script'] = '/' + phonemic_script + '/'
#         # dictionary_item['us_phonemic_script'] = '/' + us_phonemic_script + '/'
#         dictionary_item['pronunciation_word'] = download_audio('uk', pronunciation_word)
#         # dictionary_item['us_pronunciation'] = download_audio('us', us_pronunciation)
#         # jta = JsonToApkg(dictionary_item)
#         # jta.generate_apkg()
#         yield dictionary_item


class CambridgeSpider(Spider):
    name = 'cambridge'

    allowed_domains = ['dictionary.cambridge.org']
    start_urls = ['https://dictionary.cambridge.org/']
    # wayback_url = ''

    def __init__(self, q, *args, **kwargs):
        super(CambridgeSpider, self).__init__(*args, **kwargs)
        self.q = q
        self.url = args[0][0]
        self.tld = args[0][1]
        self.cid = args[0][2]
        self.in_dsense = args[0][3]

    def start_requests(self):
        # word_url = 'https://dictionary.cambridge.org/dictionary/english/' + getattr(self, 'word')
        word_url = getattr(self, 'url')
        # with open('urls.txt', 'rb') as urls:
        #     for url in urls:
        yield Request(word_url, self.parse)

    # allowed_domains = ['dictionary.cambridge.org']
    # allowed_domains = ['web.archive.org']
    # start_urls = [
    #     # 'https://dictionary.cambridge.org/dictionary/english/' + self.word,
    # ]

    def parse(self, response):
        print(response.request.headers.get('Referer', None))
        print(response.request.headers.get('User-Agent', None))
        dictionary_item = CambridgeDictionaryItem()
        tld = getattr(self, 'tld')
        cid = getattr(self, 'cid')
        in_dsense = getattr(self, 'in_dsense')
        combinators = ['', '>', '+', '~']

        if tld == "co.uk":
            accent_tld = "uk"
        else:  # tld == "com"
            accent_tld = "us"

        word = response.css(".hw.dhw").css("::text").extract_first()
        word_type = None

        for combinator in combinators:
            if in_dsense:
                word_type = response.css(f"#{cid}{combinator} .dsense_h .dsense_pos").css("::text").extract_first()
            else:
                section_id = '-'.join(cid.split('-', 2)[:2])
                word_type = response.css(f"#{section_id}{combinator} .dpos-h .dpos").css("::text").extract_first()
            # print(f"#{cid}{combinator} .dpos-h .dpos")
            if word_type is not None:
                # print("correct")
                break
        print(word_type)
        meaning = None
        for combinator in combinators:
            if in_dsense:
                meaning = response.css(f"#{cid}{combinator} .dsense_b .db").css("::text").extract()
            else:
                meaning = response.css(f"#{cid}{combinator} .dphrase_b .db").css("::text").extract()
            # print(f"#{cid}{combinator} .dpos-h .dpos")
            if meaning is not None:
                # print("correct")
                break
        print(meaning)
        example_sentences = None
        for combinator in combinators:
            if in_dsense:
                example_sentences = response.css(f"#{cid}{combinator} .dsense_b .deg").css("::text").extract()
            else:
                example_sentences = response.css(f"#{cid}{combinator} .dphrase_b .deg").css("::text").extract()
            # print(f"#{cid}{combinator} .dpos-h .dpos")
            if example_sentences is not None:
                # print("correct")
                break
        print(example_sentences)
        # word = response.css("#cald4-1+ .dpos-h .hw").css("::text").extract_first()
        # word_type = response.css("#cald4-1+ .dpos-h .dpos").css("::text").extract_first()
        # //div[@class="cid" and @id=cid]

        phonemic_script = response.css(f".{accent_tld} .lpl-1").css("::text").extract_first()  # todo: what if 2 audio
        synonyms = response.css(f".{accent_tld} #ampaudio2 source::attr(src)").extract_first()  # amp-audio
        # us_phonemic_script = response.css(".us .lpl-1").css("::text").extract_first()
        # pronunciation = response.css(f".{accent_tld} #ampaudio1 source::attr(src)").extract_first()  # amp-audio
        # us_pronunciation = response.css(".us #ampaudio2 source::attr(src)").extract_first()  # amp-audio

        def download_audio() -> str:
            filename = word + '_' + accent_tld + '.mp3'

            tts = gTTS(word, lang='en', tld=tld)
            tts.save(filename)

            # url = 'https://' + CambridgeSpider.allowed_domains[0] + address
            # http = urllib3.PoolManager(10, headers={'user-agent': USER_AGENT})
            # # r1 = http.urlopen('GET', 'http://httpbin.org/headers')
            # # print(r1.data)
            #
            # # 1
            # r = http.request('GET', url, preload_content=False)
            # with open(filename, 'wb') as out:
            #     while True:
            #         data = r.read(2**16)  # 65536
            #         if not data:
            #             break
            #         out.write(data)
            # r.release_conn()

            # 2
            # with http.request('GET', url, preload_content=False) as resp, open(filename, 'wb') as out_file:
            #     shutil.copyfileobj(resp, out_file)
            # resp.release_conn()

            # 3
            # with open(filename, 'wb') as out:
            #     r = http.request('GET', url, preload_content=False)
            #     shutil.copyfileobj(r, out)

            # 4
            # with http.request('GET', url, preload_content=False) as r, open(filename, 'wb') as out_file:
            #     shutil.copyfileobj(r, out_file)

            return '[sound:' + filename + ']'

        dictionary_item['word'] = word
        dictionary_item['word_type'] = word_type
        dictionary_item['meaning'] = ''.join(meaning).split(':')[0]  # todo: get diff meaning & sentences based on type
        # dictionary_item['example_sentences'] = ''.join(example_sentences).split('.')[:2]  # ''.join(example_sentences)
        dictionary_item['example_sentences'] = re.findall('.*?[.!?]', ''.join(example_sentences))[:2]
        dictionary_item['phonemic_script'] = '/' + phonemic_script + '/'
        # dictionary_item['us_phonemic_script'] = '/' + us_phonemic_script + '/'
        dictionary_item['pronunciation_word'] = download_audio()
        # dictionary_item['us_pronunciation'] = download_audio('us', us_pronunciation)
        dictionary_item['synonyms'] = word
        jta = JsonToApkg(dictionary_item)
        jta.generate_apkg()
        self.q.put([dictionary_item])
        yield dictionary_item


class MeaningsSpider(Spider):
    name = 'meanings'

    def __init__(self, q, *args, **kwargs):
        print(args)
        super(MeaningsSpider, self).__init__(*args, **kwargs)
        self.q = q
        self.url = args[0][0]

    def start_requests(self):
        print("start_requests")
        word_url = getattr(self, 'url')
        yield Request(word_url, self.parse)

    def parse(self, response):
        print(response.request.headers.get('Referer', None))
        print(response.request.headers.get('User-Agent', None))
        meanings_item = MeaningsItem()

        meanings = []
        count = 0

        # TODO: .cl, .dlu, codes, adjectives hint, language hint
        # .dexamp > .deg(.dlu separates); .ddef_d > .db(.b separates);
        # example sentences = #cid~ .dsense_b .dexamp span
        # get all sections and extract last one
        # .dsense .dsense_pos .dsense_gw        .dphrase-block
        # section  type        short meaning    block

        sections = response.css(".dsense")
        for section in sections:
            section_id = section.css(".cid::attr(id)").extract()

            # dphrase_block = section.css(".dphrase-block").extract()
            parts_of_speech = section.css(".dsense_pos").extract()
            if not parts_of_speech:
                in_dsense = False
                print('not in_dsense:', section.css(".cid::attr(id)").extract())
                word = section.css(".dphrase-title b").css("::text").extract_first()
                guide_word = ''
                part_of_speech = None
                cid = '-'.join(section_id[0].split('-', 2)[:2])
                combinators = ['', '>', '+', '~']
                for combinator in combinators:
                    part_of_speech = response.css(f"#{cid}{combinator} .dpos-h .dpos").css("::text").extract_first()
                    # print(f"#{cid}{combinator} .dpos-h .dpos")
                    if part_of_speech is not None:
                        # print("correct")
                        break
                # slice_number = 0
                # while bool(re.findall('[0-9]+', section_id[0].rsplit('-', slice_number)[0])) and part_of_speech is None:
                #     combinators = ['', '>', '+', '~']
                #     for combinator in combinators:
                #         part_of_speech = response.css(f"#{section_id[0].rsplit('-', slice_number)[0]}{combinator} "
                #                                       f".dpos-h .dpos").css("::text").extract_first()
                #         # print(f"#{section_id[0][:slice_number]}{combinator} .dpos-h .dpos")
                #         if part_of_speech is not None:
                #             # print("correct")
                #             break
                #     if slice_number is None:
                #         slice_number = 0
                #     slice_number += 1

                ## in_dsense ##
                # meanings with blue_blocks and separate cids | but remember blue_blocks have their own word :)
                # TODO: all meanings including blue_blocks with different cids
                # = #cid~ .dsense_b .ddef_d  (cald4-1-1, cald4-1-3, cald4-2-5?parent, cald4-2-6?parent,
                # cald4-2-10?parent)
                # != #cid~ .dsense_b .db
                # TODO: all meanings excluding blue_blocks with different cids
                # = #cid~ .dsense_b > .ddef_block .ddef_d  (cald4-1-1, cald4-1-3)
                # != #cid~ .dsense_b > .ddef_block .db
                # TODO: specific blue_block meaning with cid | parent doesn't have meaning but blue_block with cid does
                # = #cid~ .dphrase_b .ddef_d  (cald4-1-1-4, cald4-1-1-5, cald4-1-3-3, cald4-2-5-1?child,
                # cald4-2-6-1?child, cald4-2-10-1?child)
                # != #cid~ .dphrase_b .db

                # without blue_blocks
                # TODO: all meanings
                # = #cid~ .dsense_b .ddef_d  (cald4-1-2, cald4-1-4, cald4-1-5, cald4-1-6, cald4-1-7, cald4-1-10,
                # cald4-2-1, cald4-2-2, cald4-2-3, cald4-2-4, )
                # = #cid~ .dsense_b .db


                ## not in_dsense ##
                # in blue_block
                # it can be related to previous word in_dsense
                # it has two cids where 2nd points to meaning
                # TODO: meaning
                # = #cid~ .dphrase_b .ddef_d  (cald4-1-9-1, )
                # != #cid~ .dphrase_b .db

                ## cbed ##
                # = #cid~ .dsense_b .ddef_d  (cbed-1-1, ..., cbed-1-8, )

                if word is None:
                    word = response.css(".hw.dhw").css("::text").extract_first()
                    domain = section.css(".ddomain").css("::text").extract()
                    word_meaning = section.css(".db").css("::text").extract()
                    dlu = section.css(".dlu").css("::text").extract()
                    cl = section.css(".cl").css("::text").extract()
                    if domain:
                        word += f" ({'/'.join(domain)})"
                        if dlu:
                            word += f" ({'/'.join(dlu)})"
                        if cl:
                            word += f" ({' '.join(cl)})"
                    elif dlu:
                        word = f"{'/'.join(dlu)}"
                        if cl:
                            word += f" ({' '.join(cl)})"
                    elif cl:
                        word = f"{' '.join(cl)}"
                    else:
                        word += f" ({''.join(word_meaning).split(':')[0]})"
            else:
                in_dsense = True
                # {'cid': ['cald4-1-1', 'cald4-1-1-4', 'cald4-1-1-5'], 'word': 'run', 'gw': '(GO QUICKLY)', 'pos': 'verb',
                #  'in_dsense': True}
                # {'cid': ['cald4-1-4'], 'word': 'run', 'gw': '(FLOW)', 'pos': 'verb', 'in_dsense': True}
                # {'cid': ['cald4-1-3', 'cald4-1-3-3'], 'word': 'run', 'gw': '(OPERATE)', 'pos': 'verb',
                #  'in_dsense': True}
                # {'cid': ['cacd-1-2'], 'word': 'run', 'gw': '(TRAVEL/GO)', 'pos': 'verb', 'in_dsense': True}
                # {'cid': ['cald4-2-5', 'cald4-2-5-1'], 'word': 'run', 'gw': '(SERIES)', 'pos': 'noun', 'in_dsense': True}
                # {'cid': ['cald4-2-10', 'cald4-2-10-1'], 'word': 'run', 'gw': '(ILLNESS)', 'pos': 'noun',
                #  'in_dsense': True}
                # {'cid': ['cald4-2-2'], 'word': 'run', 'gw': '(TRAVEL)', 'pos': 'noun', 'in_dsense': True}

                # if len(section_id) > 1:
                #   check if there is a meaning
                #   if no meaning found then:
                #     go in other block and make the word main!
                #   else meaning found then:
                #     create another instance of the block
                # else:
                #   check if there is a meaning
                #   if no meaning found then:
                #     ignore this word
                #   else meaning found then:
                #     keep this word

                # if word has multiple meanings:
                #   create another instances of those meanings
                print('in_dsense:', section.css(".cid::attr(id)").extract())
                b = section.css("b").css("::text").extract()
                word = section.css(".dsense_hw").css("::text").extract_first()
                guide_word = '(' + section.css(".dsense_gw span::text").extract_first() + ')'
                if b:
                    if guide_word:
                        guide_word += f" ({' '.join(b)})"
                    else:
                        guide_word = f" ({' '.join(b)})"
                part_of_speech = section.css(".dsense_pos::text").extract_first()
                # definitions = section.css(".ddef_d").css("::text").extract()
                # sentences = section.css(".deg").css("::text").extract()
            if word is not None:
                word = re.sub("\s\s+", " ", word)
            if guide_word is not None:
                guide_word = re.sub("\s\s+", " ", guide_word)
            meanings.append({'cid': section_id, 'word': word, 'gw': guide_word,
                             'pos': part_of_speech, 'in_dsense': in_dsense})
            count += 1

        print(count)
        meanings_item['meanings'] = meanings
        self.q.put([meanings_item['meanings']])
        yield meanings_item