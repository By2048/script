import re
import os
import hashlib

from rich import print
from rich import box, get_console
from rich.align import Align
from rich.live import Live
from rich.table import Table

path_folders = "D:\\"
path_icons = "D:\\#Icon"

desktop_ini_data = """
[.ShellClassInfo]
IconResource={},0
"""
desktop_ini_data = desktop_ini_data.strip('\n')

ignore_folder = ["System Volume Information", "$RECYCLE.BIN"]


def clear(folder):
    """ 清除图标缓存 - del desktop.ini """
    folder_path = os.path.join(path_folders, folder)
    desktop_ini_path = os.path.join(folder_path, 'desktop.ini')
    if not os.path.isfile(desktop_ini_path):
        return
    os.system(f" attrib -s -h \"{desktop_ini_path}\" ")
    os.remove(desktop_ini_path)


def create(folder):
    """ 设置Windows系统中文件夹显示的图标 """
    folder_path = os.path.join(path_folders, folder)
    if not os.path.isdir(folder_path):
        return

    hash_icon = hashlib.md5(folder.encode("utf-8")).hexdigest()[:6]
    hash_icon_path = f"{path_icons}\\#hash-{hash_icon}.ico"
    name_icon_path = f"{path_icons}\\{folder}.ico"

    icon_file_path = ""
    if os.path.exists(hash_icon_path):
        icon_file_path = hash_icon_path
    if os.path.exists(name_icon_path):
        icon_file_path = name_icon_path

    if not icon_file_path:
        if not re.match(r"[a-zA-Z1-9_\-]+", folder):
            return folder, f"{name_icon_path} {hash_icon_path}"

    desktop_ini_path = os.path.join(folder_path, 'desktop.ini')

    if os.path.isfile(desktop_ini_path):
        os.system(f" attrib -s -h \"{desktop_ini_path}\" ")

    try:
        with open(desktop_ini_path, 'w', encoding="utf-8") as file:
            file.write(desktop_ini_data.format(icon_file_path))
    except Exception as e:
        print(f'---------- {folder_path} - {icon_file_path} ----------')
        print(e)

    os.system(f" attrib +h +s \"{desktop_ini_path}\" ")
    os.system(f" attrib +r \"{folder_path}\" ")

    return folder_path, icon_file_path


def main():
    console = get_console()
    table = Table()

    table.add_column("Folder", justify="right", width=30)
    table.add_column("Icon", justify="left", width=30)
    table_center = Align.center(table)
    console.clear()
    print()
    print()
    with Live(table_center, console=console, refresh_per_second=30):
        for folder in os.listdir(path_folders):
            if folder in ignore_folder:
                continue
            clear(folder)
            result = create(folder)
            if not result:
                continue
            table.add_row(*result)
    print()
    print()


if __name__ == '__main__':
    main()
