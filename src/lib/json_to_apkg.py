import random
from datetime import datetime as dt

import genanki
# from aqt import mw

# https://github.com/kerrickstaley/genanki

# just do these steps
# automatic fill
# my_note = genanki.Note(
#     model=my_model,
#     # fields=[
#     #   "water", "noun", "wa..r", "/\u02c8w\u0254\u02d0.t\u0259/", "/\u02c8w\u0251\u02d0.t\u032c\u025a/",
#     #   "[sound:water_uk.mp3]", "[sound:water_us.mp3]",
#     #   "a clear liquid, without colour or taste, that falls from the sky as rain and is necessary for animal and plant life: an area of water, such as the sea, a lake, or a swimming pool: the level of an area of water: a way of referring to urine (= yellowish liquid waste from the body): the area of sea near to and belonging to a particular country: the water contained in a particular lake, river, or part of the sea: the liquid that surrounds a baby inside a pregnant woman's womb: water from a spring, especially when used in the past for drinking or swimming in, in order to improve the health: ",
#     #   "a bottle/drink/glass of water bottled/mineral/tap water hot/cold water Can I have a drop of water in my whisky, please? Is there enough hot water for a bath? The human body is about 50 percent water.The water's warm - are you coming in? I don't like getting my head under (= in) water. Dad, I swam a whole length of the pool under water (= with the whole head and body below the surface of the water)!The river is difficult to cross during periods of high water.Is there any pain when you pass water? If your water is dark, it may mean you are dehydrated.St Lucia depends on its clean coastal waters for its income.In the shallow waters of the Gulf of Mexico, oil rigs attract fish.At 3 a.m. her waters broke, and the baby was born soon after.People used to come to this city to take (= drink or swim in) the waters.Hot water circulates through the heating system.The water in the lake is so clear that you can see the bottom.The water supply is being tested for contamination.You'll dehydrate very quickly in this heat, if you don't drink lots of water.The light reflected off the surface of the water.",
#     #   "", ""]
#     fields=[
#
#     ]
# )


def generate_cloze(phrase: str):
    n = len(phrase) - phrase.count(' ')
    if (n % 2) == 0:
        u_count = int(n/2)
    else:
        u_count = int(n/2)
    phrase_list = phrase.split(' ')  # todo: what if '-' is there
    cloze_list = phrase_list.copy()
    while u_count > 0:
        temp_word = random.choice(phrase_list)
        temp_len = len(temp_word)
        if temp_len <= 1:
            # print("condition 1:", temp_len, u_count)
            u_count -= temp_len
            cloze_text = "_" * temp_len
            # cloze_list = [sub.replace(temp_word, cloze_text) for sub in phrase_list]
        else:
            # print("condition 2:", temp_len, u_count)
            if temp_len <= u_count:
                r_count = int(temp_len/2)
            else:
                r_count = u_count
            cloze_indexes = random.sample(range(0, temp_len), r_count)  # temp_word indexes
            cloze = list(temp_word)
            for idx in cloze_indexes:
                cloze[idx] = "_"
            cloze_text = ''.join(cloze)
            if temp_len > u_count:
                # print('The End!')
                u_count = 0
            else:
                # print('Not yet')
                u_count -= len(cloze_indexes)
        temp_index = cloze_list.index(temp_word)
        cloze_list[temp_index] = cloze_text
        phrase_list.remove(temp_word)
        # print(phrase_list)
        # print(cloze_list)
        # print("end of loop:", temp_len, u_count)
    return ' '.join(cloze_list)


class JsonToApkg:

    def __init__(self, j_dict):
        self.j_dict = j_dict

    def generate_apkg(self):
        # create/initialize model
        my_model = genanki.Model(
            1646879431108,  # todo: change id and also create new customized structure
            name='English Vocab',
            fields=[
                {'name': 'Word'},
                {'name': 'Type'},
                {'name': 'Cloze'},
                {'name': 'PhonemicScript'},
                {'name': 'Pronunciation'},
                {'name': 'Definition'},
                {'name': 'Sentences'},
                {'name': 'Picture'},
                {'name': 'Synonyms'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': " <div style='font-family: Segoe UI; font-size: 35px;'>{{Cloze}}</div>\n\n<div style='font-family: Segoe UI; font-size: 25px; color: green;'>{{Definition}}</div>\n</br>Type your answer here:{{type:Word}}\n<br>\n{{Picture}}\n",
                    'afmt': "{{type:Word}}\n</br>\n<div style='font-family: Segoe UI; font-size: 35px; color: blue'>{{Word}}</div>\n<div style='font-family: Segoe UI; font-size: 25px;'>{{PhonemicScript}}</div>\n</br>\n{{Pronunciation}}\n<hr id=answer>\n</br>\n<div style='font-family: Segoe UI; font-size: 23px; color: green;'>{{Definition}}</div>\n</br>\n<div style='font-family: Segoe UI; font-size: 20px; color: white;'>{{Sentences}}</div>\n</br>\n{{Synonyms}}",
                },
                {
                    'name': 'Card 2',
                    'qfmt': "TYPE WHAT YOU HEAR ------------->  {{Pronunciation}}\n</br>\n<div style='font-family: Segoe UI; font-size: 25px; color: blue'>{{PhonemicScript}}</div>\n</br>\n{{type:Word}}\n</br>\n<div style='font-family: Segoe UI; font-size: 25px; color: green;'>{{Definition}}</div>\n</br>\n{{Picture}}",
                    'afmt': "{{type:Word}}\n</br>\n<div style='font-family: Segoe UI; font-size: 35px; color: blue'>{{Word}}</div>\n<div style='font-family: Segoe UI; font-size: 25px;'>{{PhonemicScript}}</div>\n</br>\nLISTEN AGAIN ------------->  {{Pronunciation}}\n</br></br>\n<div style='font-family: Segoe UI; font-size: 25px; color: green;'>{{Definition}}</div>\n</br>\n<div style='font-family: Segoe UI; font-size: 20px; color: white;'>{{Sentences}}</div>",
                },
            ],
            css=".card {\n font-family: Segoe UI;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n#typeans { font-size:60px !important }",
        )

        # just do these steps
        # automatic fill
        # todo: cloze, picture, synonyms, arrange in order, if sound not there then?
        list_of_fields = [
            self.j_dict.get("word", ""),
            self.j_dict.get("word_type", ""),
            generate_cloze(self.j_dict["word"]),  # self.j_dict.get("cloze", ""),
            self.j_dict.get("phonemic_script", ""),
            self.j_dict.get("pronunciation_word", ""),
            self.j_dict.get("meaning", ""),
            self.j_dict.get("sentences", ""),
            "",  # self.j_dict.get("picture", ""),
            "https://www.thesaurus.com/browse/" + self.j_dict.get("synonyms", "")
        ]
        # list_of_fields = [x for x in self.j_dict.values()]

        my_note = genanki.Note(
            model=my_model,
            fields=list_of_fields
        )

        my_deck = genanki.Deck(
            1646145285163,  # todo: change id and name
            "English Vocabulary (British Accent)")
        my_deck.add_note(my_note)

        # add media
        my_package = genanki.Package(my_deck)
        my_package.media_files = [self.j_dict["pronunciation_word"][7:-1:]]
        # generate apkg
        # my_package.write_to_file('output-' + self.j_dict["word"] + '.apkg')
        # apkg_filename = 'output-' + dt.now().strftime("%Y%m%d%H%M%S") + '.apkg'
        apkg_filename = 'output' + '.apkg'
        my_package.write_to_file(apkg_filename)
        return apkg_filename

# ---------------------------------------------------
# my_package = genanki.Package(my_deck)
# my_package.media_files = ['water_uk.mp3', 'water_us.mp3']
#
# my_model = genanki.Model(
#   1091735104,
#   'Simple Model with Media',
#   fields=[
#     {'question': 'Question'},
#     {'answer': 'Answer'},
#     {'sound': '[sound:water_uk.mp3]'},                                  # ADD THIS
#   ],
#   templates=[
#     {
#       'name': 'Card 1',
#       'qfmt': '{{Question}}<br>{{MyMedia}}',              # AND THIS
#       'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
#     },
#   ])

# -------------------------------------------------AQT
# notes_in_deck = mw.col.findNotes("deck:'Country Capitals'")
# config = mw.addonManager.getConfig(__name__)
# deckname = str(config['deckname'])
# # searchterm = str('"deck:'+"'"+deckname+"'"+'"')
# # searchterm = "deck:'" + deckname + "'"
# searchterm = f"deck:'{deckname}'"
# notes_in_deck = mw.col.findNotes(searchterm)