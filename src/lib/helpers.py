import os


def get_root_path() -> str:
    if 'ANDROID_STORAGE' in os.environ:
        from android.storage import app_storage_path
        # path = f'{app_storage_path()}/'

        package_name = app_storage_path().split('/')[-2]
        path = f'/storage/emulated/0/Android/data/{package_name}/files/'
    else:  # platform == 'win'
        path = 'files/'
    return path
