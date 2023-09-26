import os
import re
import subprocess
import sys
from pathlib import WindowsPath
from pprint import pprint

from PIL import Image
from loguru import logger

from config import folders, windows_config
from config import path_icon
from model import Folder, Desktop, Lnk

try:
    from tool.file import get_exe_version, lnk_to_exe
except ImportError:
    from ..tool.file import get_exe_version, lnk_to_exe


def init_folders(filter=""):
    for win_disk in windows_config.keys():
        if not win_disk.startswith("$"):
            continue

        disk = win_disk.replace("$", "")
        disk_path = WindowsPath(disk)

        for disk_folder in windows_config[win_disk].keys():
            path_folder = disk_path / disk_folder
            if not path_folder.exists():
                continue

            if filter:
                if filter not in path_folder.as_posix():
                    continue

            desktop_config = windows_config[win_disk][disk_folder].get('Desktop')
            lnk_config = windows_config[win_disk][disk_folder].get('Lnk')

            folder = Folder()
            folder.path = path_folder
            desktop = Desktop(desktop_config)
            folder.desktop = desktop

            # 忽略Desktop前缀 直接设置参数
            # name_quick = windows_config[win_disk][disk_folder].get('DesktopName')
            # icon_quick = windows_config[win_disk][disk_folder].get('DesktopIcon')

            # if not folder.desktop.name and name_quick:
            #     folder.desktop.name = name_quick
            # if not folder.desktop.icon and icon_quick:
            #     folder.desktop.icon = icon_quick

            if not lnk_config:
                folder.lnks = []

            # Default:None \ k-v 一个快捷方式
            if lnk_config and isinstance(lnk_config, dict):
                folder.lnks = [Lnk(lnk_config)]

            # [k-v] 多个快捷方式
            if lnk_config and isinstance(lnk_config, list):
                folder.lnks = [Lnk(item) for item in lnk_config]

            folders.append(folder)