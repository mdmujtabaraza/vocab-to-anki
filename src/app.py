import logging
import os
import subprocess
import webbrowser
from datetime import datetime as dt
import time
import json
import re
import traceback

# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s:%(levelname)s:%(message)s"
# )

import bs4
import urllib3
import requests
from user_agent import generate_user_agent
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import validators
from bs4 import BeautifulSoup

from kivy.animation import Animation
from kivy import require
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.list import OneLineListItem, TwoLineListItem, OneLineIconListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDRectangleFlatButton, MDIconButton, MDFloatingActionButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelTwoLine
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.gridlayout import MDGridLayout
from kivy.config import Config
from kivy.uix.widget import Widget
from kivymd.uix.textfield import MDTextField
from kivymd.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex

from src.db import create_connection, create_table, create_tag, select_all_tags, select_tags_which_contains
from src.dict_scraper.spiders import cambridge
from src.lib.helpers import get_root_path, is_platform, check_android_permissions, request_android_permissions
from src.lib.json_to_apkg import JsonToApkg
from src.lib.strings import get_text


# os.environ["KIVY_NO_CONSOLELOG"] = "1"
# require('2.1.0')

CONTAINER = {'current_url': '', 'requests': [], 'tags': [],
             'm_checkboxes': [], 'm_checkboxes_selected': 0, 'm_checkboxes_total': 0}
DICTIONARIES = {
    get_text("cambridge"): "dictionary.cambridge.org/dictionary/english/",
    get_text("dictionary_com"): "dictionary.com/browse/",
    get_text("merriam_webster"): "merriam-webster.com/dictionary/",
    get_text("oxford"): "oxfordlearnersdictionaries.com/definition/english/",
    get_text("vocabulary_com"): "vocabulary.com/dictionary/",
}
HEADERS = {
    'User-Agent': generate_user_agent(device_type='smartphone' if is_platform('android') else 'desktop'),
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
        # todo: if cambridgespider in this part then except
        # headers = {'User-Agent': session.headers['User-Agent'], 'Referer': 'https://www.google.com'}
        # TODO: select random URL
        # TODO: if bad response on selecting cached 1st goto original. if error on 1st goto cached
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


class MeaningsPanelContent(MDGridLayout):
    def __init__(self, *args, **kwargs):
        super().__init__()
        parent_checkbox = args[0]
        meaning = args[1]
        section_ids = meaning['cid']
        more_words = meaning['more_words'][section_ids[0]]
        for key, value in more_words.items():
            # root.ids.meanings_screen.ids.meanings_panel
            section_tuple = (section_ids, (key, value), meaning['pos'], meaning['in_dsense'])
            child_checkbox = MeaningMDCheckbox(section_tuple)
            # menu_screen = self.root.get_screen("menu_screen")
            menu_screen_instance = MDApp.get_running_app().menu_screen_instance
            self.add_widget(OneLineListItem(
                text=value,
                # on_release=lambda x, y=section_tuple: menu_instance.confirm_generation(y)
                on_release=lambda x, y=child_checkbox: menu_screen_instance.change_checkbox_state(y)
            ))
            for index in range(len(CONTAINER['m_checkboxes'])):
                cbox = CONTAINER['m_checkboxes'][index]
                if type(cbox) is list and cbox[0] == parent_checkbox:
                    CONTAINER['m_checkboxes'][index].append(child_checkbox)
                    break

            self.add_widget(child_checkbox)


class MeaningMDCheckbox(MDCheckbox):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.section_tuple = args[0]
        self.active = False
        if self.section_tuple is not None:
            CONTAINER['m_checkboxes_total'] += 1

    def on_checkbox_active(self, checkbox, value):
        # print(getattr(self, 'some_data'))
        print("On Active:", checkbox)
        try:
            CONTAINER['m_checkboxes'].index(checkbox)
        except ValueError:
            print("list")
            for cbox in CONTAINER['m_checkboxes']:
                if type(cbox) is list:
                    if checkbox == cbox[0]:
                        print('in cbox[0]')
                        for child_cbox in cbox[1:]:
                            if value != child_cbox.active:
                                child_cbox.active = value
                        break
                    elif checkbox in cbox:
                        print('in child')
                        CONTAINER['m_checkboxes_selected'] = CONTAINER['m_checkboxes_selected']+1 \
                            if value else CONTAINER['m_checkboxes_selected']-1
                        if value:
                            if all([x.active for x in cbox[1:]]):
                                cbox[0].active = value
                        else:
                            if not any([x.active for x in cbox[1:]]):
                                cbox[0].active = value
                        break
        else:
            print("not list")
            CONTAINER['m_checkboxes_selected'] = CONTAINER['m_checkboxes_selected'] + 1 \
                if value else CONTAINER['m_checkboxes_selected'] - 1
        finally:
            # if value:
            #     print('The checkbox', checkbox, 'is active', 'and', checkbox.state, 'state')
            # else:
            #     print('The checkbox', checkbox, 'is inactive', 'and', checkbox.state, 'state')
            pass
        MDApp.get_running_app().on_selected()

        # for checkbox in CONTAINER['m_checkboxes']:
        #     print(checkbox)


class IconListItem(OneLineIconListItem):
    icon = StringProperty()


class MenuScreen(MDScreen):
    def __init__(self, **kwargs):
        # call grid layout constructor
        super(MenuScreen, self).__init__(**kwargs)
        self.dictionary_menu = None
        self.tags_menu = None
        self.dialog = None
        self.menu = None
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
        #     on_release=self.show_meanings
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

    def check_it_down(self, label_obj, lang):
        if lang == "us":
            self.ids.check_us.active = True
        elif lang == 'uk':
            self.ids.check_uk.active = True
        else:
            pass

    def tags_input_focus_mode(self, is_focussed):
        if is_focussed:
            MDApp.get_running_app().open_tags_dropdown()
        else:
            if self.tags_menu:
                self.tags_menu.dismiss()

    def open_dictionary_dropdown(self):
        if self.dictionary_menu is not None:
            self.dictionary_menu.dismiss()

        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": get_text("cambridge"),
                "on_release": lambda x=get_text("cambridge"): self.browse_dictionary(x)
            },
            {
                "viewclass": "OneLineListItem",
                "text": get_text("dictionary_com"),
                "on_release": lambda x=get_text("dictionary_com"): self.browse_dictionary(x)
            },
            {
                "viewclass": "OneLineListItem",
                "text": get_text("merriam_webster"),
                "on_release": lambda x=get_text("merriam_webster"): self.browse_dictionary(x)
            },
            {
                "viewclass": "OneLineListItem",
                "text": get_text("oxford"),
                "on_release": lambda x=get_text("oxford"): self.browse_dictionary(x)
            },
            {
                "viewclass": "OneLineListItem",
                "text": get_text("vocabulary_com"),
                "on_release": lambda x=get_text("vocabulary_com"): self.browse_dictionary(x)
            }
        ]
        self.dictionary_menu = MDDropdownMenu(
            caller=self.ids.dict_dropdown,
            items=menu_items,
            position='center',
            width_mult=4,
            max_height=dp(248),
        )
        self.dictionary_menu.open()

    def browse_dictionary(self, dictionary_name):
        webbrowser.open('https://' + DICTIONARIES[dictionary_name])
        # self.ids.url_label.text = "https://dictionary.cambridge.org/"
        # self.toast('Copied!')
        # pyperclip.copy("Convert url to cambridge")

    def toast(self, text='', duration=2.5):
        if is_platform('android'):
            toast(text=text, gravity=80, length_long=duration)
        else:
            toast(text=text, duration=duration)

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def open_apkg(self, obj):
        path = get_root_path()
        apkg_filename = 'output' + '.apkg'

        # print(apkg_filename)
        # if platform.system() == 'Darwin':  # macOS
        #     subprocess.call(('open', path + apkg_filename))
        if is_platform('win'):  # Windows
            os.startfile(os.path.join(path[:-1], apkg_filename))
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

    def generate_flashcards(self, btn):
        selected_checkboxes = []
        for checkbox in CONTAINER['m_checkboxes']:
            if type(checkbox) is list:
                for child_checkbox in checkbox[1:]:
                    if child_checkbox.active:
                        selected_checkboxes.append(child_checkbox)
            else:
                if checkbox.active:
                    selected_checkboxes.append(checkbox)

        notes = []
        jta = JsonToApkg()
        soup = get_webpage(CONTAINER['current_url'])
        for checkbox in selected_checkboxes:
            extracted_dictionary = cambridge.CambridgeSpider(
                soup, self.tld, checkbox.section_tuple
            ).parse()
            notes.append(jta.generate_note(extracted_dictionary, CONTAINER['tags']))
        # ToDo: Add a database row of tag if not exists
        # print(CONTAINER['tags'])
        for tag in CONTAINER['tags']:
            try:
                create_tag(MDApp.get_running_app().db_connection, (tag,))
            except Exception as e:
                print(e)
                print(traceback.format_exc())
            # print("inserted")
        apkg_filename = jta.generate_apkg(notes)

        MDApp.get_running_app().soft_restart()
        self.dialog_popup(
            get_text("open_confirmation"),
            get_text("flashcards_generated"),
            open_=True
        )

    def confirm_generation(self):
        # meaning = section_tuple[1]
        # meaning_text = meaning[1] if type(meaning) is tuple else meaning
        # menu_screen = self.root.get_screen("menu_screen")
        confirm_button = MDRaisedButton(
            text="CONFIRM", on_release=lambda x: self.generate_flashcards(x)
        )
        close_button = MDFlatButton(text="CLOSE", on_release=self.close_dialog)
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title=get_text("confirm_generation"),
            text=get_text("flashcards_generate"),
            buttons=[close_button, confirm_button]
        )
        self.dialog.open()

    def change_checkbox_state(self, checkbox):
        state = checkbox.active
        if state:
            checkbox.active = False
        else:
            checkbox.active = True

    def show_meanings(self):
        word_url = self.ids.word_input.text.split('#')[0].split('?')[0]
        CONTAINER['tags'] = self.ids.tags_input.text.split()
        dict_name = None
        if not validators.url(word_url):
            self.toast(get_text("url_not_found"))
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
            if not check_android_permissions():
                self.dialog.dismiss()
                MDApp.get_running_app().soft_restart()
                return False
            MDApp.get_running_app().create_tables()
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
                self.toast(get_text("invalid_url"))
                return False
            # CONTAINER['meanings'] = extracted_meanings
            # self.dialog_popup("Processing...", "Please wait. Generating Flashcard..")
            meanings_screen = self.manager.get_screen("meanings_screen")
            count = 0
            for meaning in extracted_meanings:
                section_ids = meaning['cid']
                word = meaning['word']
                guide_word = meaning['gw']
                part_of_speech = meaning['pos']
                meaning_text = word + " " + guide_word
                section_tuple = (section_ids, meaning_text, meaning['pos'], meaning['in_dsense'])
                if not meaning['more_words'][section_ids[0]]:
                    checkbox = MeaningMDCheckbox(section_tuple)
                    meanings_screen.ids.meanings_selection_list.add_widget(
                        TwoLineListItem(
                            text=meaning_text,
                            secondary_text=f"{part_of_speech}",
                            # on_release=lambda x, y=section_tuple: self.confirm_generation(y)
                            on_release=lambda x, y=checkbox: self.change_checkbox_state(y)
                        )
                    )
                    # print("Outside:", checkbox)
                    meanings_screen.ids.meanings_selection_list.add_widget(checkbox)
                    CONTAINER['m_checkboxes'].append(checkbox)
                else:
                    checkbox = MeaningMDCheckbox(None)
                    CONTAINER['m_checkboxes'].append([checkbox])
                    meanings_screen.ids.meanings_selection_list.add_widget(
                        MDExpansionPanel(
                            content=MeaningsPanelContent(checkbox, meaning),
                            panel_cls=MDExpansionPanelTwoLine(
                                text=f"{' '*4}{word} {guide_word}",
                                secondary_text=f"{' '*4}{part_of_speech}"
                            )
                        )
                    )
                    meanings_screen.ids.meanings_selection_list.add_widget(checkbox)

                count += 1
            self.dialog.dismiss()
            MDApp.get_running_app().change_screen()
        else:
            self.toast(get_text("invalid_url"))
            self.dialog.dismiss()
            return False
        # self.add_widget(MDLabel(
        #     text=f"Successfully generated flashcard for {word_url}..",
        #     halign='center', theme_text_color='Hint', font_style='OVERLINE'
        # ))

        # clear the input boxes
        # self.ids.word_input.text = ""
        return True


class MeaningsScreen(MDScreen):
    def __init__(self, **kwargs):
        # call grid layout constructor
        super(MeaningsScreen, self).__init__(**kwargs)
        # self.on_start()

    def select_all(self):
        print("Select_all")
        count = 0
        for checkbox in CONTAINER['m_checkboxes']:
            if type(checkbox) is list:
                checkbox[0].active = True
                for child_checkbox in checkbox[1:]:
                    count += 1
            else:
                count += 1
                checkbox.active = True
        CONTAINER['m_checkboxes_selected'] = count
        menu_screen_instance = MDApp.get_running_app().menu_screen_instance
        # md_bg_color = self.theme_cls.primary_color
        # left_action_items = [["arrow-left", lambda x: self.get_running_app().soft_restart()]]
        right_action_items = [[get_text("export_icon"), lambda x: menu_screen_instance.confirm_generation()],
                              [get_text("select_none_icon"), lambda x: self.deselect_all()]]
        self.ids.toolbar.right_action_items = right_action_items
        # meanings_screen.ids.toolbar.title = get_text("app_title")
        # meanings_screen.ids.toolbar.anchor_title = 'center'

    def deselect_all(self):
        print("Select_None")
        for checkbox in CONTAINER['m_checkboxes']:
            if type(checkbox) is list:
                checkbox[0].active = False
            else:
                checkbox.active = False
        CONTAINER['m_checkboxes_selected'] = 0
        right_action_items = [[get_text("select_all_icon"), lambda x: self.select_all()]]
        self.ids.toolbar.right_action_items = right_action_items

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

    # def on_start(self):
    #     # for i in range(20):
    #     #     self.ids.meanings_selection_list.add_widget(
    #     #         OneLineListItem(text=f"Single-line item {i}")
    #     #     )
    #     self.ids.box.add_widget(
    #         MDToolbar(
    #             type_height="medium",
    #             # headline_text=f"Headline",
    #             left_action_items=[[get_text("back_icon"), lambda x: x]],
    #             right_action_items=[
    #                 ["attachment", lambda x: x],
    #                 ["calendar", lambda x: x],
    #                 ["dots-vertical", lambda x: x],
    #             ],
    #             title="Title"
    #         )
    #     )


class MyApp(MDApp):
    # overlay_color = get_color_from_hex("#6042e4")
    menu_screen_instance = MenuScreen()
    meanings_screen_instance = MeaningsScreen()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = Builder.load_file("src/app.kv")
        self.db_connection = None

    def build(self):
        Window.bind(on_keyboard=self._on_keyboard_handler)
        # sm.add_widget(MenuScreen(name='menu_screen'))
        # sm.add_widget(MeaningsScreen(name='meanings_screen'))
        self.title = get_text("app_title")
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.material_style = "M3"
        return self.screen
        # return sm
        # return MyLayout()

    def on_start(self):
        print('Starting...')
        print("Size:", Window.size)
        request_android_permissions()

    def restart(self):
        self.root.clear_widgets()
        self.stop()
        global CONTAINER
        CONTAINER['current_url'] = ''
        CONTAINER['tags'] = []
        CONTAINER['m_checkboxes'] = []
        CONTAINER['m_checkboxes_selected'] = 0
        CONTAINER['m_checkboxes_total'] = 0
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
        print('Restarting..')
        global CONTAINER
        CONTAINER['current_url'] = ''
        CONTAINER['tags'] = []
        CONTAINER['m_checkboxes'] = []
        CONTAINER['m_checkboxes_selected'] = 0
        CONTAINER['m_checkboxes_total'] = 0
        request_android_permissions()

        meanings_screen = self.root.get_screen("meanings_screen")
        meanings_screen.ids.toolbar.title = get_text("app_title")
        meanings_screen.ids.toolbar.anchor_title = 'center'
        if meanings_screen.ids.toolbar.right_action_items[0][0] == get_text("export_icon"):
            meanings_screen.ids.toolbar.right_action_items.pop(0)
            # meanings_screen.ids.toolbar.right_action_items = \
            #     [[get_text("select_all_icon"), lambda x: self.get_running_app().meanings_screen_instance.select_all()]]
        meanings_screen.ids.meanings_selection_list.clear_widgets()
        self.root.transition.direction = 'right'
        self.root.transition.duration = 0.5  # 0.5 second
        self.root.current = 'menu_screen'
        # self.change_screen()

    def create_tables(self):
        if self.db_connection is not None:
            return True
        db_path = f'{get_root_path()}data.db'
        self.db_connection = create_connection(db_path)
        # https://stackoverflow.com/a/44951682
        sql_create_tags_table = """
                                CREATE TABLE IF NOT EXISTS tags(
                                tag TEXT NOT NULL COLLATE NOCASE,
                                PRIMARY KEY(tag)
                                )
                                """
        create_table(self.db_connection, sql_create_tags_table)

        # https://www.designcise.com/web/tutorial/how-to-do-case-insensitive-comparisons-in-sqlite
        # Without a COLLATE INDEX our queries will do a full table scan
        # EXPLAIN QUERY PLAN SELECT * FROM tags WHERE tag = 'some-tag;
        # output: SCAN TABLE tags
        # When COLLATE NOCASE index is present, the query does not scan all rows.
        # EXPLAIN QUERY PLAN SELECT * FROM tags WHERE tag = 'some-tag';
        # output: SEARCH TABLE tags USING INDEX idx_nocase_tags (tag=?)
        sql_create_tags_index = """
                                CREATE INDEX IF NOT EXISTS idx_nocase_tags ON tags (tag COLLATE NOCASE)
                                """
        create_table(self.db_connection, sql_create_tags_index)
        return True

    # def callback(self, button):
    #     Snackbar(text="Hello World").open()

    # def set_selection_mode(self, instance_selection_list, mode):
    #     meanings_screen = self.root.get_screen("meanings_screen")
    #     if mode:
    #         md_bg_color = self.theme_cls.primary_dark
    #         left_action_items = [
    #             [
    #                 "close",
    #                 lambda x: meanings_screen.ids.meanings_selection_list.unselected_all(),
    #             ]
    #         ]
    #         right_action_items = [["dots-vertical"]]
    #     else:
    #         md_bg_color = self.theme_cls.primary_color
    #         left_action_items = [["arrow-left", lambda x: self.get_running_app().soft_restart()]]
    #         right_action_items = [["dots-vertical"]]
    #         meanings_screen.ids.toolbar.title = get_text("app_title")
    #         meanings_screen.ids.toolbar.anchor_title = 'center'
    #
    #     Animation(md_bg_color=md_bg_color, d=0.2).start(meanings_screen.ids.toolbar)
    #     meanings_screen.ids.toolbar.left_action_items = left_action_items
    #     meanings_screen.ids.toolbar.right_action_items = right_action_items

    def _on_keyboard_handler(self, instance, key, *args):
        # print(key, chr(key))
        menu_screen = self.root.get_screen("menu_screen")

        if menu_screen.ids.tags_input.focus:
            menu_screen_instance = self.get_running_app().menu_screen_instance
            if menu_screen_instance.tags_menu:
                menu_screen_instance.tags_menu.dismiss()
            if key == 8:
                self.open_tags_dropdown()
            else:
                self.open_tags_dropdown(chr(key))
                # CONTAINER['tags_input_text'] = CONTAINER['tags_input_text'][:-1]
            # elif key == 32:
            #     CONTAINER['tags_input_text'] = ''
            # else:
            #     CONTAINER['tags_input_text'] += chr(key)

    def open_tags_dropdown(self, key=None):
        if not check_android_permissions():
            self.soft_restart()
            return False
        self.create_tables()
        menu_screen = self.root.get_screen("menu_screen")
        menu_screen_instance = self.get_running_app().menu_screen_instance
        menu_items = []
        try:
            typed_tag = menu_screen.ids.tags_input.text.split()[-1] if key is None \
                else menu_screen.ids.tags_input.text.split()[-1] + key
        except IndexError:
            typed_tag = ''
        # print("typed_tag:", typed_tag)
        if not typed_tag:
            rows = select_all_tags(self.db_connection)
        else:
            rows = select_tags_which_contains(self.db_connection, typed_tag)
        for row in rows:
            some_dict = {
                "viewclass": "IconListItem",
                "icon": get_text("tag_icon"),
                "height": dp(56),
                "text": row[0],
                "on_release": lambda x=row[0]: self.set_tag(x),
            }
            menu_items.append(some_dict)
        menu_screen_instance.tags_menu = MDDropdownMenu(
            caller=menu_screen.ids.tags_input,
            items=menu_items,
            position='auto',
            ver_growth='up' if is_platform('android') else 'down',
            width_mult=4,
        )
        menu_screen_instance.tags_menu.open()

    def set_tag(self, tag):
        menu_screen = self.root.get_screen("menu_screen")
        menu_screen_instance = self.get_running_app().menu_screen_instance

        tags = menu_screen.ids.tags_input.text
        if ' ' in tags:
            tags_list = tags.split()
            tags_list[-1] = tag
            tags = ' '.join(tags_list)
        else:
            tags = tag

        menu_screen.ids.tags_input.text = tags + ' '
        menu_screen_instance.tags_menu.dismiss()
        menu_screen.ids.tags_input.focus = True

    def on_selected(self):
        meanings_screen = self.root.get_screen("meanings_screen")
        export_button = \
            [get_text("export_icon"), lambda x: self.get_running_app().menu_screen_instance.confirm_generation()]
        if CONTAINER['m_checkboxes_selected'] == 0:
            meanings_screen.ids.toolbar.title = get_text("app_title")
            meanings_screen.ids.toolbar.anchor_title = 'center'
            print('popping')
            if meanings_screen.ids.toolbar.right_action_items[0][0] == get_text("export_icon"):
                meanings_screen.ids.toolbar.right_action_items.pop(0)
                # meanings_screen.ids.toolbar.right_action_items = \
                #     [[get_text("select_all_icon"), lambda x: self.get_running_app().meanings_screen_instance.select_all()]]
        else:
            meanings_screen.ids.toolbar.title = \
                f"{CONTAINER['m_checkboxes_selected']}/{CONTAINER['m_checkboxes_total']} selected"
            meanings_screen.ids.toolbar.anchor_title = 'left'

            print('going inside')
            if meanings_screen.ids.toolbar.right_action_items[0][0] != get_text("export_icon"):
                print('inside')
                meanings_screen.ids.toolbar.right_action_items.insert(0, export_button)
            print('outside')
            # meanings_screen.ids.toolbar.right_action_items = [["select-off", lambda x: meanings_screen.deselect_all()]]

    # def on_unselected(self, instance_selection_list, instance_selection_item):
    #     meanings_screen = self.root.get_screen("meanings_screen")
    #     if instance_selection_list.get_selected_list_items():
    #         meanings_screen.ids.toolbar.title = str(
    #             len(instance_selection_list.get_selected_list_items())
    #         )


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
