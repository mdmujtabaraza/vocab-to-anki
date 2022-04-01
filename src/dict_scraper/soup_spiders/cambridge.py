import re

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
import requests


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
    def __init__(self, q, headers, *args, **kwargs):
        # print(args)
        self.q = q
        self.headers = headers
        self.url = args[0][0]
        self.tld = args[0][1]
        self.section_tuple = args[0][2]
        self.result = requests.get(self.url, headers=self.headers)
        self.soup = BeautifulSoup(self.result.text, "html.parser")

    def parse(self):
        # print(response.request.headers.get('Referer', None))
        # print(response.request.headers.get('User-Agent', None))

        meanings = []
        count = 0

        sections = self.soup.select(".dsense")
        print(len(sections))
        last_true_section_id = None
        for section in sections:
            section_id = get_tree(section, set())
            more_words = {section_id[0]: {}}

            parts_of_speech = section.select(".dsense_pos")
            if not parts_of_speech:
                in_dsense = False
                print('not in_dsense:', section_id)
                word = extract_text(section.select_one(".dphrase-title b"))
                guide_word = ''
                part_of_speech = self.soup.select_one(f"#{section_id[0]} ~ .dpos-h .dpos")
                if not part_of_speech:
                    # print("pos None")
                    if last_true_section_id.split('-')[0] == section_id[0].split('-')[0]:
                        part_of_speech = extract_text(self.soup.select_one(f"#{last_true_section_id} ~ .dsense_h .dsense_pos"))
                        # print("last")
                    else:
                        cid = '-'.join(section_id[0].split('-', 2)[:2])
                        part_of_speech = extract_text(self.soup.select_one(f"#{cid} ~ .dpos-h .dpos"))
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
        self.q.put([meanings])



