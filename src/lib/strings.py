"""
src.lib.strings
By default, uses `en-gb.json` file inside the `strings` top-level folder.
If language changes, set `src.lib.strings.default_locale` and run `src.lib.strings.refresh()`.
"""
import json

default_locale = "en-us"
cached_strings = {}


def refresh():
    global cached_strings
    with open(f"strings/{default_locale}.json") as f:
        cached_strings = json.load(f)


def get_text(name):
    return cached_strings[name]


refresh()
