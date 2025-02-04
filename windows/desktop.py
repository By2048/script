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
    from tool.file import get_exe_file_version, get_exe_product_version, lnk_to_exe
except ImportError:
    from ..tool.file import get_exe_file_version, get_exe_product_version, lnk_to_exe


# $Name \ Folder | Name
def get_desktop_name(folder: Folder):
    name = ""
    if folder.desktop.name and folder.desktop.name != folder.path.name:
        if folder.desktop.name.startswith("$"):
            name = folder.desktop.name.lstrip('$')
        else:
            name = f"{folder.path.name} | {folder.desktop.name}"
    return name


def get_desktop_icon(folder: Folder):
    #

    icon = WindowsPath()
    desktop = folder.desktop

    # 图片格式转换
    def png2ico(png: WindowsPath):
        ico = png.with_suffix(".ico")
        image = Image.open(png)
        image.save(ico)
        return ico

    # 绝对路径 D:\App\Xxx.exe
    if desktop.icon and ":\\" in str(desktop.icon):
        icon = WindowsPath(desktop.icon)
        if icon.exists():
            return icon

    # 使用当前文件夹中的设置 | Folder\Xxx{exe|ico}
    if desktop.icon and "$" not in str(desktop.icon):
        if str(desktop.icon).endswith((".exe", ".ico")):
            if (icon := folder.path / desktop.icon).exists():
                return icon

    # 在默认位置寻找图标并支持png转ico D:\#Icon\Folder{ico|png}
    if desktop.icon and "$" in str(desktop.icon):
        desktop.icon = WindowsPath(str(desktop.icon).replace("$", ""))
        ico_file = path_icon / f"{desktop.icon}.ico"
        png_file = path_icon / f"{desktop.icon}.png"
        if ico_file.exists():
            icon = ico_file
        elif png_file.exists():
            icon = png2ico(png_file)
        return icon

    # 默认设置 相对路径 | 使用软件所在文件夹中的信息 | Folder\Folder{exe|ico|png}
    exe_file = folder.path / f"{folder.path.name}.exe"
    ico_file = folder.path / f"{folder.path.name}.ico"
    if exe_file.exists():
        return exe_file
    elif ico_file.exists():
        return ico_file


def get_desktop_info(folder: Folder):
    #

    # 文件夹信息
    def get_info_by_exe(folder, info):
        # 软件版本信息
        if not info.lower().endswith(".exe"):
            return
        mode = "$File"
        exe = ""
        version = ""
        if " | " in info:
            mode = info.split(" | ")[0]
            exe = info.split(" | ")[-1]
            exe = folder.path / exe
        else:
            exe = folder.path / info
        if mode in ["$File", "$file"]:
            version = get_exe_file_version(exe.as_posix())
        if mode in ["$Product", "$product"]:
            version = get_exe_product_version(exe.as_posix())

        if version:
            return version

    def get_info_by_cmd(folder, info):
        # 执行指定命名获取的版本
        # cmd | frpc.exe -v | (\d+) | \1
        if not info.lower().startswith("$cmd |"):
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

    def get_info_by_name(folder, info):
        # 执行指定命名获取的版本
        # name | envs\spyder-runtime\conda-meta | spyder-*-py*.json | (spyder-)([\d\w\.]+)(.*.json) | 2

        if not info.lower().startswith("$name |"):
            return

        _folder = info.split("|")[1].strip()
        _glob = info.split("|")[2].strip()
        _match = info.split("|")[3].strip()
        _get = info.split("|")[4].strip()
        _get = int(_get) if _get.isdigit() else None

        if ":\\" not in _folder:
            _folder = folder.path / _folder

        folder_path = WindowsPath(_folder)
        if not folder_path.exists():
            return ""

        file_info: WindowsPath | None = None
        for path in folder_path.glob(_glob):
            if path.is_file():
                file_info = path

        if not file_info:
            return ""

        try:
            obj = re.search(_match, str(file_info.name)).group(_get)
        except AttributeError:
            obj = ""

        if obj:
            return obj

    def get_info_by_file(folder, info):
        # 指定文件内容
        # file | .\ventoy\version | ([\d\.]+) | 1
        if not info.lower().startswith("$file |"):
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
        if not info.lower().startswith("$count |"):
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
            version = get_exe_file_version(_exe_)
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
        info_name = get_info_by_name(folder, info)
        info_count = get_info_by_count(folder, info)

        info_content.append(info_exe)
        info_content.append(info_cmd)
        info_content.append(info_name)
        info_content.append(info_file)
        info_content.append(info_count)

        # 原始数据
        if not any([info_exe, info_cmd, info_name, info_file, info_count]):
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
    table.add_column("Folder", justify="center", width=30)
    table.add_column("Icon", justify="center", width=30)
    table.add_column("Info", justify="center", width=25)
    table.add_column("Name", justify="center", width=20)
    return table


def get_desktop_table_line(folder: Folder):
    _folder_ = folder.path
    _icon_ = folder.desktop.icon or ""
    _info_ = folder.desktop.info or ""
    _name_ = folder.desktop.name or ""

    _folder_ = str(_folder_) + "\\"
    _icon_ = str(_icon_)
    _info_ = str(_info_)
    _name_ = str(_name_)

    if _folder_ in _icon_:
        _icon_ = _icon_.replace(_folder_, "")

    if " > " in _info_:
        _info_ = _info_.split(" > ")[0].strip()
    if " | " in _info_:
        _info_ = _info_.split(" | ")[-1].strip()

    if " | " in _name_:
        _name_ = _name_.split(" | ")[-1].strip()
    if " > " in _name_:
        _name_ = _name_.split(" > ")[-1].strip()

    line = [_folder_, _icon_, _info_, _name_]
    line = [str(item) for item in line]

    return line


def create_ini_file(folder: Folder):
    desktop = folder.desktop

    desktop_ini_data = "[.ShellClassInfo]"
    if desktop.icon:
        desktop_ini_data += f"\nIconResource = {desktop.icon} , 0"
    if desktop.info:
        desktop_ini_data += f"\nInfoTip = {desktop.info}"
    if desktop.name:
        desktop_ini_data += f"\nLocalizedResourceName = {desktop.name}"
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
        folder.desktop.name = get_desktop_name(folder)
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
            if not folder.desktop:
                continue
            line = get_desktop_table_line(folder)
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