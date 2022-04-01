import os
import platform
import subprocess
import webbrowser
from datetime import datetime as dt
import time
import json
import re

import urllib3
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import validators
import requests_random_user_agent
from bs4 import BeautifulSoup
from kivy import platform as kplatform
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDRectangleFlatButton, MDIconButton, MDFloatingActionButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelTwoLine
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.gridlayout import MDGridLayout
from kivy.config import Config
from kivy.uix.widget import Widget
from kivymd.uix.textfield import MDTextField
from kivymd.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex

from src.dict_scraper.spiders import cambridge

# os.environ["KIVY_NO_CONSOLELOG"] = "1"
# kivy.require('1.9.0')

CONTAINER = {'current_url': '', 'requests': []}
DICTIONARIES = {
    "Cambridge": "https://dictionary.cambridge.org/dictionary/english/",
    "Dictionary.com": "https://www.dictionary.com/browse/",
    "Merriam-Webster": "https://www.merriam-webster.com/dictionary/",
    "Oxford": "https://www.oxfordlearnersdictionaries.com/definition/english/",
    "Vocabulary.com": "https://www.vocabulary.com/dictionary/",
}
HEADERS = {
    'Referer': 'https://www.google.com'
}

session = requests.Session()
# session.headers.update(HEADERS)
# retry = Retry(total=5, connect=3, backoff_factor=0.5)
# adapter = HTTPAdapter(max_retries=retry)
# session.mount('http://', adapter)
# session.mount('https://', adapter)

http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=1.0, read=2.0))


def get_webpage(word_url):
    r_text = None
    global CONTAINER
    for request in CONTAINER['requests']:
        if word_url in request[0]:
            r_text = request[1]
            # print("Found")
            break
    if not r_text:
        headers = {'User-Agent': session.headers['User-Agent'], 'Referer': 'https://www.google.com'}
        # TODO: select random URL
        # TODO: if bad response on selcting cached 1st goto original. if error on 1st goto cached
        try:
            response = http.request('GET', word_url, headers=headers, retries=urllib3.Retry(5, redirect=2))
        except:
            gcurl = "https://webcache.googleusercontent.com/search?q=cache:" + word_url
            response = http.request('GET', gcurl, headers=headers, retries=urllib3.Retry(5, redirect=2))
        r_text = response.data
        print(response.status)

        # print(session.headers['User-Agent'], session.headers['Referer'])
        # r_text = session.get(word_url, verify=False).text

        CONTAINER['requests'].append((word_url, r_text))
    return r_text

# ----------------------------------- KIVY -------------------------------------

# Window.size = (500, 400)


class MeaningsPanelContent(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__()
        menu_instance = args[0]
        meaning = args[1]
        section_ids = meaning['cid']
        more_words = meaning['more_words'][section_ids[0]]
        for key, value in more_words.items():
            # root.ids.meanings_screen.ids.meanings_panel
            section_tuple = (section_ids, (key, value), meaning['pos'], meaning['in_dsense'])
            self.add_widget(OneLineListItem(
                text=value,
                on_release=lambda x, y=section_tuple: menu_instance.confirm_generation(y)
            ))


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        # call grid layout constructor
        super(MenuScreen, self).__init__(**kwargs)
        self.dropdown_menu = None
        self.dialog = None
        self.tld = 'com'
        self.timestamp = dt.now().strftime("%Y%m%d%H%M%S")

        # set columns
        # self.cols = 1
        # self.row_force_default = True
        # self.row_default_height = 120
        # self.col_force_default = True
        # self.col_default_width = 100

        # create a second GridLayout
        # self.top_grid = MDGridLayout(
        #     row_force_default=True,
        #     row_default_height=40,
        #     col_force_default=True,
        #     col_default_width=100
        # )
        # self.top_grid.cols = 2

        # add widgets
        # icon_label = MDIcon(icon='magnify', halign='center')
        # self.top_grid.add_widget(icon_label)
        # self.add_widget(MDLabel(  # .top_grid.
        #     text="",
        #     halign='center',
        #     theme_text_color='Primary',
        #     font_style='Body1',
        #     pos_hint={'center_x': 0.5, 'center_y': 0.7}
        #     # size_hint_x=None,
        #     # size_hint_y=None,
        #     # height=50,
        #     # width=200
        # ))
        # add input box
        # self.word = MDTextField(
        #     multiline=False,
        #     pos_hint={'center_x': 0.5, 'center_y': 0.5},
        #     size_hint_x=None, width=300
        # )
        # self.word_url = Builder.load_string(word_url_helper)
        # self.add_widget(self.word_url)  # .top_grid.

        # self.drop_down = Builder.load_string(dropdown_helper)
        # self.add_widget(self.drop_down)

        # add the new grid to our app
        # self.add_widget(self.top_grid)

        # create a submit button
        # self.submit = MDRectangleFlatButton(
        #     text='Submit',
        #     pos_hint={'center_x': 0.5, 'center_y': 0.4},
        #     on_release=self.show_data
        # )
        # bind the button
        # self.submit.bind(on_press=self.press)
        # self.add_widget(self.submit)

    # def change_screen(self):
    #     if self.manager.current == "meanings_screen":
    #         self.manager.transition.direction = 'right'
    #         self.manager.transition.duration = 0.5
    #         self.manager.current = "menu_screen"
    #     else:
    #         # sm.current = 'meanings_screen'
    #         self.manager.transition.direction = 'left'
    #         self.manager.transition.duration = 0.5
    #         self.manager.current = 'meanings_screen'

    def open_dropdown(self, dict_dropdown=False):
        if self.dropdown_menu is not None:
            self.dropdown_menu.dismiss()

        if dict_dropdown:
            self.menu_list = [
                {
                    "viewclass": "OneLineListItem",
                    "text": "Cambridge",
                    "on_release": lambda x="Cambridge": self.browse_dictionary('Cambridge')
                },
                {
                    "viewclass": "OneLineListItem",
                    "text": "Dictionary.com",
                    "on_release": lambda x="Dictionary.com": self.browse_dictionary('Dictionary.com')
                },
                {
                    "viewclass": "OneLineListItem",
                    "text": "Merriam-Webster",
                    "on_release": lambda x="Merriam-Webster": self.browse_dictionary('Merriam-Webster')
                },
                {
                    "viewclass": "OneLineListItem",
                    "text": "Oxford",
                    "on_release": lambda x="Oxford": self.browse_dictionary('Oxford')
                },
                {
                    "viewclass": "OneLineListItem",
                    "text": "Vocabulary.com",
                    "on_release": lambda x="Vocabulary.com": self.browse_dictionary('Vocabulary.com')
                },
                # {
                #     "viewclass": "OneLineListItem",
                #     "text": "Back",
                #     "on_release": lambda x="Back": self.open_dropdown(dict_dropdown=True)
                # }
            ]
        else:
            self.menu_list = [
                {
                    "viewclass": "OneLineListItem",
                    "text": "Word",
                    "on_release": lambda x="Word": self.find_word()
                },
                {
                    "viewclass": "OneLineListItem",
                    "text": "Phrase",
                    "on_release": lambda x="Phrase": self.find_idiom()
                },
                {
                    "viewclass": "OneLineListItem",
                    "text": "Idiom",
                    "on_release": lambda x="Idiom": self.find_idiom()
                },
                {
                    "viewclass": "OneLineListItem",
                    "text": "Phrasal Verb",
                    "on_release": lambda x="Phrasal Verb": self.find_idiom()
                },
                {
                    "viewclass": "OneLineListItem",
                    "text": "Collocation",
                    "on_release": lambda x="Collocation": self.find_idiom()
                }
            ]
        self.dropdown_menu = MDDropdownMenu(
            caller=self.ids.dict_dropdown,
            items=self.menu_list,
            width_mult=4
        )
        self.dropdown_menu.open()

    def find_word(self):
        self.open_dropdown()

    def find_idiom(self):
        print("idiom is pressed")

    def browse_dictionary(self, dictionary_name):
        webbrowser.open(DICTIONARIES[dictionary_name])
        # self.ids.url_label.text = "https://dictionary.cambridge.org/"
        # self.toast('Copied!')
        # pyperclip.copy("Convert url to cambridge")

    def toast(self, text='', duration=2.5):
        if kplatform == 'android':
            toast(text=text, gravity=80, length_long=duration)
        else:
            toast(text=text, duration=duration)

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def open_apkg(self, obj):
        # todo: use kivymd android platform statement/variable
        # print("Okay.")
        apkg_filename = 'output' + '.apkg'
        # print(apkg_filename)
        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', apkg_filename))
        elif platform.system() == 'Windows':  # Windows
            os.startfile(apkg_filename)
        else:  # linux variants
            subprocess.call(('xdg-open', apkg_filename))

    def dialog_popup(self, title, text, close=False, open_=False):
        if not self.dialog:
            pass
        else:
            self.dialog.dismiss()
        open_button = MDRaisedButton(text="OPEN", on_release=self.open_apkg)
        close_button = MDFlatButton(text="CLOSE", on_release=self.close_dialog)
        if close:
            self.dialog = MDDialog(
                title=title,
                text=text,
                # size_hint=(0.7, 1),
                buttons=[close_button]
            )
        elif open_:
            self.dialog = MDDialog(
                title=title,
                text=text,
                # size_hint=(0.7, 1),
                buttons=[close_button, open_button]
            )
        else:
            self.dialog = MDDialog(
                title=title,
                text=text,
                # size_hint=(0.7, 1)
            )
        self.dialog.open()

    def checkbox_click(self, instance, value, tld):
        if value is True:
            self.tld = tld

    def confirm_generation(self, section_tuple):
        meaning = section_tuple[1]
        meaning_text = meaning[1] if type(meaning) is tuple else meaning
        confirm_button = MDRaisedButton(
            text="CONFIRM", on_release=lambda x, y=section_tuple: self.generate_flashcard(x, y)
        )
        close_button = MDFlatButton(text="CLOSE", on_release=self.close_dialog)
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title="Confirm generation",
            text=f"Do you want to generate Anki flashcard for \"{meaning_text}\"?",
            # size_hint=(0.7, 1),
            buttons=[close_button, confirm_button]
        )
        self.dialog.open()

    def generate_flashcard(self, btn, section_tuple):
        print(section_tuple)
        r_text = get_webpage(CONTAINER['current_url'])
        extracted_dictionary = cambridge.CambridgeSpider(
            BeautifulSoup(r_text, "html.parser"), self.tld, section_tuple
        ).parse()
        MDApp.get_running_app().soft_restart()
        self.dialog_popup(
            "Open Anki Package?",
            f"Successfully generated flashcard. Do you want to open it in Anki?",
            open_=True
        )

    def show_data(self):
        # word_url = self.word_url.text
        word_url = self.ids.word_input.text
        dict_name = None

        if not validators.url(word_url):
            self.toast("URL not found. Please try again")
            return False
        # todo: extract word from word_url
        # url_list = word_url.split('/')
        # word = url_list[-2] if not url_list[-1] else url_list[-1]
        # print it to the screen
        # self.add_widget(MDLabel(
        #     text=f"Processing {word_url}..", halign='center', theme_text_color='Hint', font_style='Caption'
        # ))
        # todo: decide which spider
        # runner = CrawlerRunner({
        #     'USER_AGENT': USER_AGENT
        #     # 'FEED_FORMAT': 'csv',
        #     # 'FEED_URI': 'output.csv',
        #     # 'DEPTH_LIMIT': 2,
        #     # 'CLOSESPIDER_PAGECOUNT': 3,
        # })
        for name, dict_url in DICTIONARIES.items():
            if dict_url in word_url:
                dict_name = name
                break
        if dict_name:
            # d = runner.crawl(
            #     CambridgeSpider,
            #     url=word_url,
            #     tld=self.tld
            #     # urls_file='input.txt'
            # )
            # d = runner.join()
            # d.addBoth(lambda _: reactor.stop())
            # try:
            #     wburl = "https://archive.org/wayback/available?url=" + word_url
            #     response = requests.get(wburl, headers={"user-agent": SPIDER_SETTINGS['USER_AGENT']}, verify=False)
            #     data = response.json()
            #     archived_snapshots = data['archived_snapshots']
            #     # todo: implement keyerror instead
            #     wayback_url = archived_snapshots['closest']['url']
            # except KeyError:
            #     self.toast("Invalid URL. Please try again")
            #     return False

            # gcurl = "https://webcache.googleusercontent.com/search?q=cache:" + word_url
            CONTAINER['current_url'] = word_url
            r_text = get_webpage(word_url)
            extracted_meanings = cambridge.MeaningsSpider(BeautifulSoup(r_text, "html.parser")).parse()
            # CONTAINER['meanings'] = extracted_meanings

            # self.dialog_popup("Processing...", "Please wait. Generating Flashcard..")
            meanings_screen = self.manager.get_screen("meanings_screen")
            for meaning in extracted_meanings:
                section_ids = meaning['cid']
                word = meaning['word']
                guide_word = meaning['gw']
                part_of_speech = meaning['pos']
                meaning_text = word + " " + guide_word
                section_tuple = (section_ids, meaning_text, meaning['pos'], meaning['in_dsense'])
                if not meaning['more_words'][section_ids[0]]:
                    meanings_screen.ids.meanings_container.add_widget(
                        TwoLineListItem(
                            text=meaning_text,
                            secondary_text=f"{part_of_speech}",
                            on_release=lambda x, y=section_tuple: self.confirm_generation(y)
                        )
                    )
                else:
                    meanings_screen.ids.meanings_container.add_widget(
                        MDExpansionPanel(
                            content=MeaningsPanelContent(self, meaning),
                            panel_cls=MDExpansionPanelTwoLine(
                                text=f"{' '*4}{word} {guide_word}",
                                secondary_text=f"{' '*4}{part_of_speech}"
                            )
                        )
                    )
            MDApp.get_running_app().change_screen()
        else:
            self.toast("Invalid URL. Please try again")
            return False
        # self.add_widget(MDLabel(
        #     text=f"Successfully generated flashcard for {word_url}..",
        #     halign='center', theme_text_color='Hint', font_style='OVERLINE'
        # ))

        # clear the input boxes
        self.ids.word_input.text = ""
        return True


class MeaningsScreen(Screen):
    def __init__(self, **kwargs):
        # call grid layout constructor
        super(MeaningsScreen, self).__init__(**kwargs)
        # self.on_start()

    # def change_screen(self):
    #     if self.manager.current == "menu_screen":
    #         self.manager.transition.direction = 'left'
    #         self.manager.transition.duration = 0.5  # 0.5 second
    #         self.manager.current = "meanings_screen"
    #     else:
    #         # sm.current = 'menu_screen'
    #         self.manager.transition.direction = 'right'
    #         self.manager.transition.duration = 0.5  # 0.5 second
    #         self.manager.current = 'menu_screen'

    def on_start(self):
        # for i in range(20):
        #     self.ids.meanings_container.add_widget(
        #         OneLineListItem(text=f"Single-line item {i}")
        #     )
        self.ids.box.add_widget(
            MDToolbar(
                type_height="medium",
                # headline_text=f"Headline",
                left_action_items=[["arrow-left", lambda x: x]],
                right_action_items=[
                    ["attachment", lambda x: x],
                    ["calendar", lambda x: x],
                    ["dots-vertical", lambda x: x],
                ],
                title="Title"
            )
        )


class MyApp(MDApp):
    def build(self):
        # sm.add_widget(MenuScreen(name='menu_screen'))
        # sm.add_widget(MeaningsScreen(name='meanings_screen'))
        self.title = 'Vocab to Anki'
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.material_style = "M3"
        screen = Builder.load_file("src/app.kv")
        return screen
        # return sm
        # return MyLayout()

    def restart(self):
        self.root.clear_widgets()
        self.stop()
        global CONTAINER
        CONTAINER['current_url'] = ''
        return MyApp().run()

    def change_screen(self):
        if self.root.current == "menu_screen":
            self.root.transition.direction = 'left'
            self.root.transition.duration = 0.5  # 0.5 second
            self.root.current = "meanings_screen"
        else:
            # sm.current = 'menu_screen'
            self.root.transition.direction = 'right'
            self.root.transition.duration = 0.5  # 0.5 second
            self.root.current = 'menu_screen'

    def soft_restart(self):
        global CONTAINER
        CONTAINER['current_url'] = ''
        self.root.transition.direction = 'right'
        self.root.transition.duration = 0.5  # 0.5 second
        self.root.current = 'menu_screen'


# Run the App
if __name__ == "__main__":
    # Config.set('kivy', 'log_enable', 1)
    # # path of the log directory
    # Config.set('kivy', 'log_dir', 'C:/Users/Public/Downloads')
    # # filename of the log file
    # # Config.set('kivy', 'log_name', "anything_you_want_%y-%m-%d_%_.log")
    # Config.set('kivy', 'log_name', "anything_you_want.log")
    # # Keep log_maxfiles recent logfiles while purging the log directory.
    # # Set ‘log_maxfiles’ to -1 to disable logfile purging (eg keep all logfiles).
    # Config.set('kivy', 'log_maxfiles', 1000)
    # # minimum log level which is what you need to not see kivy's default info logs
    # Config.set('kivy', 'log_level', 'critical')
    # # apply all these changes
    # Config.write()
    # creating the object root for ButtonApp() class
    # root = ButtonApp()

    # run function runs the whole program
    # i.e run() method which calls the target
    # function passed to the constructor.
    # root.run()
    # TutorialApp().run()
    pass
