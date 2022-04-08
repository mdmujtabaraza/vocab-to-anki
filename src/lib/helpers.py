import os
import re

from bs4.element import ResultSet, Tag
from kivy import platform


def is_platform(os_name) -> bool:
    return os_name == platform


def get_root_path() -> str:
    if is_platform('android'):  # if 'ANDROID_STORAGE' in os.environ:
        from android.storage import app_storage_path
        # path = f'{app_storage_path()}/'
        package_name = app_storage_path().split('/')[-2]
        path = f'/storage/emulated/0/Android/data/{package_name}/files/'
    else:  # platform == 'win'
        path = 'files/'
    if not os.path.exists(path + 'media/'):
        os.makedirs(path + 'media/')
    return path


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


def check_android_permissions() -> bool:
    if is_platform('android'):
        from android.permissions import check_permission
        return check_permission('android.permission.WRITE_EXTERNAL_STORAGE')
    else:
        return True


def request_android_permissions():
    if is_platform('android'):
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])


def print_android_storage_path():
    if is_platform('android'):
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
