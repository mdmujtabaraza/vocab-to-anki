import os
import subprocess
import webbrowser
from datetime import datetime as dt
import time
import json
import re
import traceback

import bs4
import urllib3
import requests
from user_agent import generate_user_agent
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import validators
from bs4 import BeautifulSoup
from kivy import require, platform
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
require('2.1.0')

CONTAINER = {'current_url': '', 'requests': [], 'meanings':[]}
DICTIONARIES = {
    "Cambridge": "dictionary.cambridge.org/dictionary/english/",
    "Dictionary.com": "dictionary.com/browse/",
    "Merriam-Webster": "merriam-webster.com/dictionary/",
    "Oxford": "oxfordlearnersdictionaries.com/definition/english/",
    "Vocabulary.com": "vocabulary.com/dictionary/",
}
HEADERS = {
    'User-Agent': generate_user_agent(device_type='smartphone' if 'ANDROID_STORAGE' in os.environ else 'desktop'),
    'Referer': 'https://www.google.com'
}

print(HEADERS)

session = requests.Session()
session.headers.update(HEADERS)
retry = Retry(total=5, connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=1.0, read=2.0))


def remove_http_www(url):
    if 'http' in url:
        url = url.split('//')[1]
    if 'www' in url:
        url = re.sub('www.', '', url)
    return url


def get_webpage(word_url, extract_meanings=False):
    url = remove_http_www(word_url)
    soup = None
    meanings = None
    found = False
    global CONTAINER
    for request in CONTAINER['requests']:
        if url == request[0]:
            print("Found")
            found = True
            soup = request[1]
            meanings = request[2]
            break
    if not found:
        # todo: if cambidgespider in this part then except
        # headers = {'User-Agent': session.headers['User-Agent'], 'Referer': 'https://www.google.com'}
        # TODO: select random URL
        # TODO: if bad response on selcting cached 1st goto original. if error on 1st goto cached
        try:
            response = session.get(word_url)
        except:
            gcurl = "https://webcache.googleusercontent.com/search?q=cache:" + word_url
            response = session.get(gcurl)
            url = gcurl
        print(response.status_code)
        soup = BeautifulSoup(response.text, "lxml")
        if extract_meanings:
            meanings = cambridge.MeaningsSpider(soup).parse()
            CONTAINER['requests'].append([url, soup, meanings])

        # print(session.headers['User-Agent'], session.headers['Referer'])
        # r_text = session.get(word_url, verify=False).text

    return meanings if extract_meanings else soup


def clear_request(word_url=None):
    global CONTAINER
    if not word_url:
        CONTAINER['requests'] = []
        return True
    url = remove_http_www(word_url)
    for request in CONTAINER['requests']:
        if url == request[0]:
            print("Found")
            CONTAINER['requests'].remove(request)
            return True
    return False

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
        webbrowser.open('https://' + DICTIONARIES[dictionary_name])
        # self.ids.url_label.text = "https://dictionary.cambridge.org/"
        # self.toast('Copied!')
        # pyperclip.copy("Convert url to cambridge")

    def toast(self, text='', duration=2.5):
        if platform == 'android':
            toast(text=text, gravity=80, length_long=duration)
        else:
            toast(text=text, duration=duration)

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def open_apkg(self, obj):
        # todo: use kivymd android platform statement/variable
        # todo: root path one place of android
        if 'ANDROID_STORAGE' in os.environ:
            from android.storage import app_storage_path
            # path = f'{app_storage_path()}/'
            package_name = app_storage_path().split('/')[-2]
            path = f'/storage/emulated/0/Android/data/{package_name}/files/'
        else:
            path = 'files'
        # path = 'files/'
        apkg_filename = 'output' + '.apkg'
        # print(apkg_filename)
        # if platform.system() == 'Darwin':  # macOS
        #     subprocess.call(('open', path + apkg_filename))
        if platform == 'win':  # Windows
            os.startfile(os.path.join(path, apkg_filename))
        else:  # linux variants
            try:
                from jnius import cast
                from jnius import autoclass

                PythonActivity = autoclass('org.kivy.android.PythonActivity')  # request the Kivy activity instance
                Intent = autoclass('android.content.Intent')
                String = autoclass('java.lang.String')
                Uri = autoclass('android.net.Uri')
                # fileNameJava = cast('java.lang.CharSequence', String(path + apkg_filename))
                File = autoclass('java.io.File')
                FileProvider = autoclass('android.support.v4.content.FileProvider')

                currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
                ctx = currentActivity.getApplicationContext()

                filePath = File(path + apkg_filename)
                uriApkg = FileProvider.getUriForFile(ctx, f"{ctx.getPackageName()}.file_provider", filePath)
                urifromfile = Uri.fromFile(filePath)
                parcelable = cast('android.os.Parcelable', urifromfile)

                target = Intent()
                # target.setType('*/*')
                target.setAction(Intent.ACTION_VIEW)
                target.setDataAndType(uriApkg, "application/apkg")  # setData(urifromfile)
                # target.putExtra(f"{ctx.getPackageName()}.extra.PATH_URI", parcelable)
                target.setFlags(Intent.FLAG_ACTIVITY_FORWARD_RESULT)
                target.setFlags(Intent.FLAG_ACTIVITY_PREVIOUS_IS_TOP)
                target.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                # intent = Intent.createChooser(target, 'Abrir el archivo')

                currentActivity.startActivity(target)

                # PythonActivity = autoclass('org.kivy.android.PythonActivity')
                # currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
                # context = cast('android.content.Context', currentActivity.getApplicationContext())
            except Exception as e:
                print("Jnius autoclass failed!", e)
                print(traceback.format_exc())
            # subprocess.call(('xdg-open', path + apkg_filename))

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
        soup = get_webpage(CONTAINER['current_url'])
        extracted_dictionary = cambridge.CambridgeSpider(
            soup, self.tld, section_tuple
        ).parse()
        MDApp.get_running_app().soft_restart()
        self.dialog_popup(
            "Open Anki Package?",
            f"Successfully generated flashcard. Do you want to open it in Anki?",
            open_=True
        )

    def show_data(self):
        word_url = self.ids.word_input.text.split('#')[0].split('?')[0]
        dict_name = None
        if not validators.url(word_url):
            self.toast("URL not found. Please try again")
            self.dialog.dismiss()
            return False
        # word_url = self.word_url.text
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
            extracted_meanings = get_webpage(word_url, extract_meanings=True)
            # extracted_meanings = get_extracted_meanings(soup)
            if not extracted_meanings:
                clear_request(word_url)
                self.dialog.dismiss()
                self.toast("Invalid URL. Please try again")
                return False
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
            self.dialog.dismiss()
            MDApp.get_running_app().change_screen()
        else:
            self.toast("Invalid URL. Please try again")
            self.dialog.dismiss()
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

    def on_start(self):
        if platform == 'android':
            try:
                from android.storage import app_storage_path
                settings_path = app_storage_path()
                print("settings_path", settings_path)

                from android.storage import primary_external_storage_path
                primary_ext_storage = primary_external_storage_path()
                print("primary_ext_storage", primary_ext_storage)

                from android.storage import secondary_external_storage_path
                secondary_ext_storage = secondary_external_storage_path()
                print("secondary_ext_storage", secondary_ext_storage)
            except Exception as e:
                print("Error printing paths", e)

            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

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
        meanings_screen = self.root.get_screen("meanings_screen")
        meanings_screen.ids.meanings_container.clear_widgets()
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
