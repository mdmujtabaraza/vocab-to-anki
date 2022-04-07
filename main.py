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

import os
from glob import glob

import ssl

from src.app import MyApp
from src.db import connection
from src.lib.helpers import get_root_path


if __name__ == '__main__':
    if 'ANDROID_STORAGE' in os.environ:
        try:
            from android import loadingscreen

            loadingscreen.hide_loading_screen()
        except Exception as e:
            print("Loading screen is not removed", e)
    ssl._create_default_https_context = ssl._create_unverified_context
    MyApp().run()

    # Delete Files on exit.
    root_path = get_root_path()
    mp3_files = glob(root_path + 'media/*.mp3')
    for f in mp3_files:
        os.remove(f)
    os.remove(root_path + 'output.apkg')

    connection.close()
