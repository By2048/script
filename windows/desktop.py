import re
import os
import sys
import ctypes
import time

import win32api
import subprocess
from pathlib import WindowsPath
from win32comext.shell import shell, shellcon

from pathlib import WindowsPath

from PIL import Image
from loguru import logger
from rich.align import Align
from rich.live import Live
from rich.table import Table

from config import folders, windows_config, console
from config import path_icon
from model import Folder, Desktop, Lnk

try:
    from tool.file import get_exe_version, lnk_to_exe
except ImportError:
    from ..tool.file import get_exe_version, lnk_to_exe


def get_desktop_icon(folder: Folder):
    desktop = folder.desktop

    icon = None

    # 在默认位置寻找图标并支持png转ico D:\#Icon\Xxx.ico
    if desktop.icon and "." not in desktop.icon:
        ico_file = path_icon / f"{desktop.icon}.ico"
        png_file = path_icon / f"{desktop.icon}.png"
        if ico_file.exists():
            icon = ico_file
        elif png_file.exists():
            image = Image.open(png_file)
            image.save(ico_file)
            icon = ico_file
        return icon

    # 在相对位置和默认位置寻找图标
    if desktop.icon and ".ico" in desktop.icon:
        icon = folder.path / desktop.icon
        if icon.exists():
            return icon

    # 使用软件中默认的图标 Folder\Xxx.exe
    if desktop.icon and ".exe" in desktop.icon:
        exe_icon = folder.path / desktop.icon
        if exe_icon.exists():
            return exe_icon

    # 使用自定义文件夹对应的默认图标 *Default
    ico_file = path_icon / f"{folder.path.name}.ico"
    if ico_file.exists():
        return ico_file
    png_file = path_icon / f"{folder.path.name}.png"
    if png_file.exists() and not ico_file.exists():
        image = Image.open(png_file)
        image.save(ico_file)
        return ico_file

    # 使用软件默认图标
    exe_file = folder.path / f"{folder.path.name}.exe"
    if exe_file.exists():
        return exe_file

    return icon


def get_desktop_info(folder: Folder):
    # 文件夹信息
    def get_info_by_exe(folder, info):
        # 软件版本信息
        if not info.lower().endswith(".exe"):
            return
        _exe_ = folder.path / info
        version = get_exe_version(_exe_.as_posix())
        if version:
            return version

    def get_info_by_cmd(folder, info):
        # 执行指定命名获取的版本
        # cmd | frpc.exe -v | (\d+) | \1
        if not info.lower().startswith("cmd |"):
            return
        _info = info.split("|")
        _info = [item.strip() for item in _info]
        _cmd = _info[1]
        # 判断绝对路径 相对路径
        if ":\\" not in _cmd:
            _cmd = _cmd.lstrip(".\\")
            _cmd = f"{folder.path}\\{_cmd}"
        _match = _info[2]
        _get = _info[3]
        _get = int(_get) if _get.isdigit() else None

        result = subprocess.Popen(_cmd, shell=True,
                                  stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        result_out = result.stdout.readlines()
        result_err = result.stderr.readlines()
        result = result_out or result_err
        try:
            result = [item.decode() for item in result]
        except Exception as e:
            result = []
        result = "".join(result)

        try:
            obj = re.search(_match, result).group(_get)
        except AttributeError:
            obj = ""

        if obj:
            return obj

    def get_info_by_file(folder, info):
        # 指定文件内容
        # file | .\ventoy\version | ([\d\.]+) | 1
        if not info.lower().startswith("file |"):
            return
        _info = info.split("|")
        _info = [item.strip() for item in _info]
        _file_path = _info[1]
        _match = _info[2]
        _get = _info[3]

        if ":\\" not in _file_path:
            _file_path = folder.path / _file_path

        _get = int(_get) if _get.isdigit() else None

        with open(_file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            obj = re.search(_match, content).group(_get)

        if obj:
            return obj

    def get_info_by_count(folder, info):
        # 文件数量
        if not info.lower().startswith("count |"):
            return
        _info = info.split("|")
        _info = [item.strip() for item in _info]
        rule = _info[1]
        total = 0
        if " " in rule:
            all_rule = rule.split()
        else:
            all_rule = [rule]
        for _rule in all_rule:
            files = list(folder.path.glob(_rule))
            total += len(files)
        total = f"{total} {rule}"
        return total

    info = folder.desktop.info

    # 尝试使用默认配置进行解析
    if not info:
        _exe_ = folder.path / f"{folder.path.name}.exe"
        if _exe_.exists():
            version = get_exe_version(_exe_)
            return version

    all_info = []
    if isinstance(info, str):
        all_info = [info.strip()]
    if isinstance(info, list):
        all_info = [item.strip() for item in info]

    info_content = []

    for info in all_info:
        info_exe = get_info_by_exe(folder, info)
        info_cmd = get_info_by_cmd(folder, info)
        info_file = get_info_by_file(folder, info)
        info_count = get_info_by_count(folder, info)

        info_content.append(info_exe)
        info_content.append(info_cmd)
        info_content.append(info_file)
        info_content.append(info_count)

        if not info_exe and not info_cmd and not info_file and not info_count:
            info_content.append(info)

        info_content = [item for item in info_content if item]

    return "  |  ".join(info_content) if info_content else ""


def get_desktop_rename(folder: Folder):
    info = {}
    rename = folder.desktop.rename
    if not rename:
        return info
    if isinstance(rename, str):
        rename = [rename]
    for item in rename:
        items = item.split("|", 1)
        key = items[0].strip()
        value = items[1].strip()
        info[key] = value
    return info


def get_desktop_table():
    table = Table()
    table.add_column("Folder", justify="left", width=30)
    table.add_column("Icon", justify="left", width=30)
    table.add_column("Info", justify="center", width=25)
    table.add_column("Name", justify="center", width=20)
    return table


def create_ini_file(folder: Folder):
    desktop = folder.desktop

    desktop_ini_data = "[.ShellClassInfo]"
    if desktop.icon:
        desktop_ini_data += f"\nIconResource = {desktop.icon} , 0"
    if desktop.info:
        desktop_ini_data += f"\nInfoTip = {desktop.info}"
    if desktop.name and desktop.name != folder.path.name:
        if desktop.name.startswith("$"):
            desktop_ini_data += f"\nLocalizedResourceName = {desktop.name.strip('$')}"
        else:
            desktop_ini_data += f"\nLocalizedResourceName = {folder.path.name} | {desktop.name}"
    if desktop.rename:
        desktop_ini_data += "\n\n[LocalizedFileNames]"
        for key, value in desktop.rename.items():
            desktop_ini_data += f"\n{key} = {value}"

    desktop_ini_data = desktop_ini_data.strip()

    desktop_ini_path = folder.path / 'desktop.ini'

    content = ""
    if desktop_ini_path.exists():
        try:
            file = open(desktop_ini_path, "r", encoding="gbk")
            content = "".join(file.readlines())
        except UnicodeDecodeError:
            pass
        finally:
            file.close()

    if desktop_ini_data == content:
        return

    try:
        os.system(f" attrib -s -h \"{desktop_ini_path}\" ")
        with open(desktop_ini_path, 'w', encoding="gbk") as file:
            file.write(desktop_ini_data)
        os.system(f" attrib +s +h \"{desktop_ini_path}\" ")
    except Exception as e:
        logger.exception(e)
    finally:
        os.system(f" attrib +r \"{folder.path.as_posix()}\" ")


def init_desktop():
    # 初始化Desktop|Lnk默认配置
    folder: Folder
    for folder in folders:
        folder.desktop.name = folder.desktop.name or folder.path.name
        folder.desktop.icon = get_desktop_icon(folder)
        folder.desktop.info = get_desktop_info(folder)
        folder.desktop.rename = get_desktop_rename(folder)


def create_desktop():
    table = get_desktop_table()
    table_center = Align.center(table)
    with Live(table_center, console=console) as live:
        folder: Folder
        for folder in folders:
            create_ini_file(folder)
            line = [f"{folder.path}\\",
                    folder.desktop.icon or "",
                    folder.desktop.info or "",
                    folder.desktop.name if folder.desktop.name != folder.path.name else ""]
            line = [str(item) for item in line]
            if not folder.desktop:
                continue
            table.add_row(*line)
            live.refresh()
            if table.row_count > console.height - 11:
                time.sleep(3)
                table.columns.clear()
                console.clear()
                console.print()
                table = get_desktop_table()
                table_center = Align.center(table)
                live.update(table_center)


def flush_desktop():
    # 刷新文件夹图片
    ctypes.windll.shell32.SHChangeNotify(
        shellcon.SHCNE_ASSOCCHANGED,
        shellcon.SHCNF_IDLIST,
        0,
        0
    )