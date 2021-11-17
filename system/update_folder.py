#
import re
import os
import sys
import hashlib
import shutil
from pathlib import Path, WindowsPath
from collections import namedtuple
from dataclasses import dataclass
import win32api
import win32com
import win32com.client

from rich import print
from rich import box, get_console
from rich.align import Align
from rich.live import Live
from rich.table import Table
from loguru import logger

try:
    from tool.file import lnk_to_exe, version
except ImportError:
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(path)
    from tool.file import lnk_to_exe, version

path_folders = WindowsPath("D:\\")
path_icons = WindowsPath("D:\\#Icon\\")
path_lnk = WindowsPath("D:\\#Lnk\\")

ignore_folder = ["System Volume Information", "$RECYCLE.BIN"]


@dataclass
class FolderDesktop(object):
    path: str = ""
    icon: str = ""
    info: str = ""

    def to_list(self):
        return [self.path, self.icon, self.info]

    def __repr__(self):
        return " | ".join(self.to_list())


def init():
    """ 设置Windows系统中文件夹显示的图标 """

    def lnk_to_exe(file: str):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(file)
        result = shortcut.Targetpath
        return result

    def get_exe_version(file: str):
        try:
            info = win32api.GetFileVersionInfo(file, os.sep)
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            high = win32api.HIWORD
            low = win32api.LOWORD
            result = f"{high(ms)}.{low(ms)}.{high(ls)}.{low(ls)}"
            return result
        except Exception as e:
            logger.exception(e)
            return None

    def get_icon(folder: WindowsPath):
        icon = None

        path_name_icon = path_icons / f"{folder.name}.ico"
        hash_icon = hashlib.md5(folder.name.encode("utf-8")).hexdigest()[:6]
        path_hash_icon = path_icons / f"#{hash_icon}.ico"

        if not re.fullmatch(r"^[a-zA-Z0-9_# \-\s]+", folder.name):
            if path_name_icon.exists():
                if not path_hash_icon.exists():
                    shutil.copy(path_name_icon.as_posix(), path_hash_icon.as_posix())

        if path_name_icon.exists():
            icon = path_name_icon

        if path_hash_icon.exists():
            icon = path_hash_icon

        if icon:
            return icon.as_posix()

        return icon

    def get_info(folder: WindowsPath):
        result = ""
        name = folder.name
        path_file_lnk = path_lnk / f"{name}.lnk"
        if path_file_lnk.exists():
            path_file_exe = lnk_to_exe(path_file_lnk.as_posix())
            path_file_exe = WindowsPath(path_file_exe)
            if path_file_exe.exists():
                result = get_exe_version(path_file_exe.as_posix())

        # #Version#xxx#
        if version_file := list(folder.glob("#Version#*")):
            result = version_file[0].name.split("#")[-2]

        # #Info#xxx#
        if (info_file := list(folder.glob("#Info#*"))):
            result = info_file[0].name.split("#")[-2]

        return result

    result = []

    for folder in path_folders.iterdir():
        fd = FolderDesktop()
        if folder.name in ignore_folder:
            continue

        if not folder.is_dir():
            continue

        icon = get_icon(folder)
        info = get_info(folder)

        fd.path = folder.as_posix()
        fd.icon = icon
        fd.info = info

        result.append(fd)

    return result


def clear(fd: FolderDesktop):
    """ 清除图标缓存 - del desktop.ini """

    folder_path = WindowsPath(fd.path)

    desktop_ini_path = folder_path / 'desktop.ini'

    if not desktop_ini_path.exists():
        return
    os.system(f" attrib -s -h \"{desktop_ini_path.as_posix()}\" ")
    desktop_ini_path.unlink()


def create(fd: FolderDesktop):
    def get_desktop_ini(fd: FolderDesktop):
        desktop_ini_data = """
        [.ShellClassInfo]
        """.strip()

        if fd.icon:
            desktop_ini_data = desktop_ini_data + "\n" + f"IconResource = {fd.icon}, 0"

        if fd.info:
            desktop_ini_data = desktop_ini_data + "\n" + f"InfoTip = {fd.info}"

        desktop_ini_data = desktop_ini_data.strip()
        return desktop_ini_data

    desktop_ini_path = WindowsPath(fd.path) / 'desktop.ini'

    if desktop_ini_path.exists():
        os.system(f" attrib -s -h \"{desktop_ini_path.as_posix()}\" ")

    try:
        with open(desktop_ini_path, 'w', encoding="utf-8") as file:
            desktop_ini = get_desktop_ini(fd)
            file.write(desktop_ini)
    except Exception as e:
        logger.exception(e)
        print(e)

    os.system(f" attrib +s +h \"{desktop_ini_path.as_posix()}\" ")


def main():
    console = get_console()
    table = Table()
    table.add_column("Folder", justify="left", width=30)
    table.add_column("Icon", justify="left", width=35)
    table.add_column("Info", justify="center", width=20)
    table_center = Align.center(table)
    console.clear()
    print()
    print()
    with Live(table_center, console=console, refresh_per_second=30):
        result = init()
        item: FolderDesktop
        for item in result:
            clear(item)
            create(item)
            table.add_row(*item.to_list())
    print()
    print()


def test():
    for folder in path_folders.iterdir():
        print(folder)
        pass


if __name__ == '__main__':
    # test()
    main()
