import os
import re

import requests
from gtts import gTTS
from bs4.element import ResultSet, Tag

from src.lib.helpers import get_root_path


allowed_domains = ['dictionary.cambridge.org']
start_urls = ['https://dictionary.cambridge.org/']


class SuspiciousOperation(Exception):
    """The user did something suspicious"""


def get_valid_filename(name):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = str(name).strip().replace(" ", "-")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    if s in {"", ".", ".."}:
        raise SuspiciousOperation("Could not derive file name from '%s'" % name)
    return s


def get_tree(branch, seen, *args, **kwargs):
    out = []
    for d in branch.find_all("div", class_="cid"):
        if d not in seen:
            seen.add(d)
            out.append(d["id"])
            t = get_tree(d, seen)
            if t:
                out.append(t)
    return out


def extract_text(data, join_char=''):
    strings = []
    if type(data) is ResultSet:
        if data:
            for element in data:
                for string in element.strings:
                    strings.append(repr(string)[1:-1])
    elif type(data) is Tag:
        if data:
            for string in data.strings:
                strings.append(repr(string)[1:-1])
    return join_char.join(strings)


class MeaningsSpider:
    def __init__(self, soup, *args, **kwargs):
        self.soup = soup

    def parse(self):
        # print(response.request.headers.get('Referer', None))
        # print(response.request.headers.get('User-Agent', None))

        meanings = []
        count = 0

        sections = self.soup.select(".dsense")
        for section in sections:
            section_id = get_tree(section, set())
            print(section_id)
        idiom_block = self.soup.select(".idiom-block")
        last_true_section_id = None
        for section in sections:
            section_id = get_tree(section, set())

            more_words = {section_id[0]: {}}
            # dphrase_block = section.css(".dphrase-block").extract()
            parts_of_speech = section.select(".dsense_pos")
            if not parts_of_speech:
                in_dsense = False
                print('not in_dsense:', section_id)
                if idiom_block:
                    # cid = '-'.join(section_ids[0].split('-', 2)[:2])
                    # word = extract_text(self.soup.select(f"#{cid} ~ .idiom-block b"))
                    word = extract_text(self.soup.select_one(f".idiom-block b"))
                    guide_word = '(' + extract_text(section.select(f".dsense_b .ddef_d .query"), join_char=' ') + ')'
                    part_of_speech = 'idiom'
                else:
                    word = extract_text(section.select_one(".dphrase-title b"))
                    guide_word = ''
                    part_of_speech = self.soup.select_one(f"#{section_id[0]} ~ .dpos-h .dpos")
                    # print("before not pos")
                    if not part_of_speech:
                        # print("pos None")
                        if last_true_section_id is not None:
                            if last_true_section_id.split('-')[0] == section_id[0].split('-')[0]:
                                part_of_speech = extract_text(self.soup.select_one(f"#{last_true_section_id} ~ .dsense_h .dsense_pos"))
                                # print("last")
                            else:
                                cid = '-'.join(section_id[0].split('-', 2)[:2])
                                part_of_speech = extract_text(self.soup.select_one(f"#{cid} ~ .dpos-h .dpos"))
                                # print("last not correct")
                        else:
                            cid = '-'.join(section_id[0].split('-', 2)[:2])
                            part_of_speech = extract_text(self.soup.select_one(f"#{cid} ~ .dpos-h .dpos"))
                            # print("last not correct")
                    # combinators = ['', '>', '+', '~']
                    # for combinator in combinators:
                    #     part_of_speech = response.css(f"#{cid}{combinator} .dpos-h .dpos").css("::text").extract_first()
                    #     print(f"#{cid}{combinator} .dpos-h .dpos")
                    #     if part_of_speech is not None:
                    #         print("correct")
                    #         break
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
                    if not word:
                        word = extract_text(self.soup.select_one(".hw.dhw"))
                        domain = extract_text(section.select(".ddomain"), join_char='/')
                        word_meaning = extract_text(section.select(".ddef_d"))
                        dlu = extract_text(section.select(".dlu"), join_char='/')
                        cl = extract_text(section.select(".cl"), join_char=' ')
                        if domain:
                            word += f" ({domain})"
                            if dlu:
                                word += f" ({dlu})"
                            if cl:
                                word += f" ({cl})"
                        elif dlu:
                            word = f"{dlu}"
                            if cl:
                                word += f" ({cl})"
                        elif cl:
                            word = f"{cl}"
                        else:
                            word += f" ({word_meaning.split(':')[0]})"
            else:
                in_dsense = True
                print('in_dsense:', section_id)
                last_true_section_id = section_id[0]

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
                if idiom_block:
                    # print("IDIOM")
                    # cid = '-'.join(section_ids[0].split('-', 2)[:2])
                    # word = extract_text(self.soup.select(f"#{cid} ~ .idiom-block b"))
                    word = extract_text(self.soup.select_one(f".idiom-block b"))
                    guide_word = ''
                    part_of_speech = 'idiom'
                else:
                    extracted_meanings = extract_text(section.select(".dsense_b > .ddef_block .ddef_d"))
                    meanings_list = extracted_meanings.split(':')[:-1]

                    if len(section_id) <= 1:
                        if len(meanings_list) > 1:
                            for i in range(len(meanings_list)):
                                more_words[section_id[0]][i + 1] = meanings_list[i]
                    else:
                        if meanings_list:
                            for i in range(len(meanings_list)):
                                more_words[section_id[0]][i + 1] = meanings_list[i]
                        for bid in section_id[1:]:
                            blue_block_title = extract_text(section.select(f"#{bid} ~ .dphrase_h b"))
                            if not blue_block_title:
                                blue_block_meaning = extract_text(section.select(f"#{bid} ~ .dphrase_b .ddef_d"))[:-1]
                                more_words[section_id[0]][bid] = blue_block_meaning
                            else:
                                more_words[section_id[0]][bid] = blue_block_title
                    # if word has multiple meanings:
                    #   create another instances of those meanings
                    word = extract_text(section.select_one(".dsense_hw"))
                    guide_word = '(' + extract_text(section.select_one(".dsense_gw span")) + ')'
                    # b = section.css("b").css("::text").extract()
                    # if b:
                    #     if guide_word:
                    #         guide_word += f" ({' '.join(b)})"
                    #     else:
                    #         guide_word = f" ({' '.join(b)})"
                    part_of_speech = extract_text(section.select_one(".dsense_pos"))
                    # definitions = section.css(".ddef_d").css("::text").extract()
                    # sentences = section.css(".deg").css("::text").extract()
            if word:
                word = re.sub("\s\s+", " ", word)
            if guide_word:
                guide_word = re.sub("\s\s+", " ", guide_word)
            meanings.append({'cid': section_id, 'word': word, 'gw': guide_word,
                             'pos': part_of_speech, 'in_dsense': in_dsense, 'more_words': more_words})
            count += 1

        # print(count)
        print(meanings)
        return meanings


class CambridgeSpider:
    def __init__(self, soup, *args, **kwargs):
        # print(url, headers, args)
        self.soup = soup
        self.tld = args[0]
        self.section_tuple = args[1]

    # allowed_domains = ['dictionary.cambridge.org']
    # allowed_domains = ['web.archive.org']
    # start_urls = [
    #     # 'https://dictionary.cambridge.org/dictionary/english/' + self.word,
    # ]

    def parse(self):
        # print(response.request.headers.get('Referer', None))
        # print(response.request.headers.get('User-Agent', None))
        tld = getattr(self, 'tld')
        section_tuple = getattr(self, 'section_tuple')
        section_ids = section_tuple[0]
        meaning = section_tuple[1]
        part_of_speech = section_tuple[2]
        in_dsense = section_tuple[3]

        # TODO: .cl, .dlu, codes, adjectives hint, language hint
        # .dexamp > .deg(.dlu separates); .ddef_d > .db(.b separates);
        # example sentences = #cid~ .dsense_b .dexamp span
        # get all sections and extract last one
        # .dsense .dsense_pos .dsense_gw        .dphrase-block
        # section  type        short meaning    block

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

        word = extract_text(self.soup.select_one(f".hw.dhw"))

        if in_dsense is True:
            # word = response.css(f"#{cid}~ .dsense_h .dsense_hw").css("::text").extract_first()
            if type(meaning) is tuple:
                if type(meaning[0]) is str:
                    cid = meaning[0]
                    meaning_text = extract_text(self.soup.select(f"#{cid} ~ .dphrase_b .ddef_d"))
                    sentences = self.soup.select(f"#{cid} ~ .dphrase_b .dexamp")
                else:  # type(meaning[0]) is int:
                    cid = section_ids[0]
                    meaning_text = extract_text(self.soup.select(f"#{cid} ~ .dsense_b .ddef_block:nth-child({meaning[0]}) .ddef_d"))
                    sentences = self.soup.select(f"#{cid} ~ .dsense_b .ddef_block:nth-child({meaning[0]}) .dexamp")
            else:  # type(meaning) is str:
                cid = section_ids[0]
                meaning_text = extract_text(self.soup.select(f"#{cid} ~ .dsense_b .ddef_d"))
                sentences = self.soup.select(f"#{cid} ~ .dsense_b .dexamp")
        else:  # in_dsense is False:
            if part_of_speech == 'idiom':
                word = extract_text(self.soup.select_one(f".idiom-block b"))
                # cid = '-'.join(section_ids[0].split('-', 2)[:2])
                # word = extract_text(self.soup.select(f"#{cid} ~ .idiom-block b"))
                meaning_text = extract_text(self.soup.select(f"#{section_ids[0]} ~ .dsense_b .ddef_d"))
                sentences = self.soup.select(f"#{section_ids[0]} ~ .dsense_b .dexamp")
            else:
                if len(section_ids) > 1:
                    cid = section_ids[1]
                    meaning_text = extract_text(self.soup.select(f"#{cid} ~ .dphrase_b .ddef_d"))
                    sentences = self.soup.select(f"#{cid} ~ .dphrase_b .dexamp")
                else:
                    cid = section_ids[0]
                    meaning_text = extract_text(self.soup.select(f"#{cid} ~ .dsense_b .ddef_d"))
                    sentences = self.soup.select(f"#{cid} ~ .dsense_b .dexamp")
        # print("MeaningText:", meaning_text)
        # print("Sentences:", type(sentences), len(sentences), type(sentences[0]))

        if tld == "co.uk":
            accent_tld = "uk"
        else:  # tld == "com"
            accent_tld = "us"

        combinators = ['', '>', '+', '~']
        # part_of_speech = None
        # for combinator in combinators:
        #     if in_dsense:
        #         part_of_speech = response.css(f"#{cid}{combinator} .dsense_h .dsense_pos").css("::text").extract_first()
        #     else:
        #         section_id = '-'.join(cid.split('-', 2)[:2])
        #         part_of_speech = response.css(f"#{section_id}{combinator} .dpos-h .dpos").css("::text").extract_first()
        #     # print(f"#{cid}{combinator} .dpos-h .dpos")
        #     if part_of_speech is not None:
        #         # print("correct")
        #         break
        # print(part_of_speech)
        # meaning = None
        # for combinator in combinators:
        #     if in_dsense:
        #         meaning = response.css(f"#{cid}{combinator} .dsense_b .ddef_d").css("::text").extract()
        #     else:
        #         meaning = response.css(f"#{cid}{combinator} .dphrase_b .ddef_d").css("::text").extract()
        #     # print(f"#{cid}{combinator} .dpos-h .dpos")
        #     if meaning is not None:
        #         # print("correct")
        #         break
        # print(meaning)
        # sentences = None
        # for combinator in combinators:
        #     if in_dsense:
        #         sentences = response.css(f"#{cid}{combinator} .dsense_b .deg").css("::text").extract()
        #     else:
        #         sentences = response.css(f"#{cid}{combinator} .dphrase_b .deg").css("::text").extract()
        #     # print(f"#{cid}{combinator} .dpos-h .dpos")
        #     if sentences is not None:
        #         # print("correct")
        #         break
        # print(sentences)
        # word = response.css("#cald4-1+ .dpos-h .hw").css("::text").extract_first()
        # part_of_speech = response.css("#cald4-1+ .dpos-h .dpos").css("::text").extract_first()
        # //div[@class="cid" and @id=cid]

        phonemic_script = extract_text(self.soup.select_one(f".{accent_tld} .lpl-1"))  # todo: what if 2 audio
        # us_phonemic_script = response.css(".us .lpl-1").css("::text").extract_first()
        # pronunciation = response.css(f".{accent_tld} #ampaudio1 source::attr(src)").extract_first()  # amp-audio
        # us_pronunciation = response.css(".us #ampaudio2 source::attr(src)").extract_first()  # amp-audio

        def download_audio() -> str:
            root_path = get_root_path() + 'media/'
            filename = get_valid_filename(word + '_' + accent_tld + '.mp3')
            # print(filename)
            tts = gTTS(word, lang='en', tld=tld)

            if not os.path.exists(root_path + filename):
                tts.save(root_path + filename)

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

        sentences_list = [str(tag) for tag in sentences]
        dictionary_item = {
            'word': word,
            'part_of_speech': part_of_speech,
            'meaning': meaning_text.split(':')[0],
            'sentences': ''.join(sentences_list),
            'phonemic_script': '' if not phonemic_script else '/' + phonemic_script + '/',
            'pronunciation_word': download_audio(),
            'synonyms': f"<a href='https://www.thesaurus.com/browse/{word}'>Synonyms</a>"
        }
        # dictionary_item['sentences'] = ''.join(sentences).split('.')[:2]  # ''.join(sentences)
        # dictionary_item['sentences'] = re.findall('.*?[.!?]', ''.join(sentences))[:2]
        # dictionary_item['us_phonemic_script'] = '/' + us_phonemic_script + '/'
        # dictionary_item['us_pronunciation'] = download_audio('us', us_pronunciation)
        # print("Generated.")
        return dictionary_item
