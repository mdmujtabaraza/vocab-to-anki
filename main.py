# generate other spiders
# cd ./src/
# scrapy genspider example example.com
# pip list --format=freeze > requirements.txt
# /storage/emulate/0/Download
# '/storage/emulated/0/Android/data/org.test.vocabtoanki/files/media/'
# settings_path /data/user/0/org.test.vocabtoanki/files
# /data/user/0/org.test.vocabtoanki/files
# https://pyjnius.readthedocs.io/en/stable/android.html
# plyer
# https://python-for-android.readthedocs.io/en/latest/apis/

# android.add_aars = ./support-v4-24.1.1.aar
# .buildozer/android/platform/build-arm64-v8a/dists/BVWSudoku__arm64-v8a/templates/AndroidManifest.tmpl.xml
# .buildozer\android\platform\python-for-android\pythonforandroid\bootstraps\sdl2\build\templates\AndroidManifest.tmpl.xml
# 	<activity  android:name="{{ a }}"></activity>
# 	{% endfor %}
# +		<provider
# +			android:name="android.support.v4.content.FileProvider"
# +			android:authorities="<YOUR PACKAGE NAME>"
# +			android:exported="false"
# +			android:grantUriPermissions="true">
# +		<meta-data
# +			android:name="android.support.FILE_PROVIDER_PATHS"
# +			android:resource="@xml/file_paths"/>
# +		</provider>
# 	</application>
# </manifest>
# Then create a folder named xml in the .buildozer\android\platform\python-for-android\pythonforandroid\bootstraps\sdl2\build\src\main\res directory and create a file named file_paths.xml with the following code:
# Then create a folder named xml in the .buildozer/android/platform/build-arm64-v8a/dists/BVWSudoku__arm64-v8a/build\src\main\res directory and create a file named file_paths.xml
# <?xml version="1.0" encoding="utf-8"?>
# <paths  xmlns:android="http://schemas.android.com/apk/res/android">
# 	<external-path  name="external_files"  path="Android/data/<YOUR PACKAGE NAME>/files/Pictures"  />
# </paths>

# <provider
#     android:name="android.support.v4.content.FileProvider"
#     android:authorities="org.test.vocabtoanki.file_provider"
#     android:exported="false"
#     android:grantUriPermissions="true">
# <meta-data
#     android:name="android.support.FILE_PROVIDER_PATHS"
#     android:resource="@xml/file_paths"/>
# </provider>

# <?xml version="1.0" encoding="utf-8"?>
# <paths  xmlns:android="http://schemas.android.com/apk/res/android">
#     <external-path  name="external_files"  path="Android/data/org.test.vocabtoanki/files"  />
# </paths>

# pyinstaller --noconfirm --name vocabtoanki --icon .\images\icon\vocabtoanki.ico --noconsole --onedir --windowed --add-data "C:/Users/Standard User/miniconda3/envs/vocab-to-anki/Lib/site-packages/user_agent/data;user_agent/data/" .\main.py
# --onefile --onedir --icon examples-path\demo\touchtracer\icon.ico --key='<16 chars>' --name vocabtoanki
# exe, Tree('C:\\Users\\Public\\Documents\\projects\\python\\vocab-to-anki\\'),
# python -m PyInstaller vocabtoanki.spec

# convert -background transparent "vocabtoanki_512x512.png" -define icon:auto-resize=16,24,32,48,64,72,96,128,256 "vocabtoanki.ico"

import os
from glob import glob

import ssl

from src.app import MyApp
from src.lib.helpers import get_root_path


def main():
    ssl._create_default_https_context = ssl._create_unverified_context
    MyApp().run()

    if MyApp().get_running_app().db_connection is not None:
        MyApp().get_running_app().db_connection.close()
    # Delete Files on exit.
    print('Cleaning up..')
    media_path = get_root_path(media=True)
    mp3_files = glob(os.path.join(media_path, '*.mp3'))
    for f in mp3_files:
        os.remove(f)
    root_path = get_root_path()
    if os.path.exists(os.path.join(root_path, 'output.apkg')):
        os.remove(os.path.join(root_path, 'output.apkg'))
    print('Cleaned.')


if __name__ == '__main__':
    main()
