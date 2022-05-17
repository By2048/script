# [2022-01-12]
import re
import os
import sys
import hashlib
import shutil
import time
import copy
from types import NoneType

import yaml
import tempfile
import subprocess
import win32api
import win32com
import win32com.client
from dataclasses import dataclass
from pathlib import WindowsPath
from win32comext.shell import shell, shellcon

from rich import print
from rich.pretty import pprint
from rich import box, get_console
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.live import Live
from rich.table import Table
from loguru import logger
from PIL import Image

try:
    from tool.file import lnk_to_exe, version
except ImportError:
    sys.path.append(WindowsPath(__file__).parents[1].as_posix())
    from tool.file import lnk_to_exe, exe_version


def join(loader, node):
    nodes = loader.construct_sequence(node)
    return ' '.join([item for item in nodes])


yaml.add_constructor(r'!Join', join)

console = get_console()

windows_config_path = WindowsPath('E:\\Config\\Windows.yaml')
with open(windows_config_path, encoding="utf-8") as file:
    windows_config = yaml.unsafe_load(file)

path_tmp = WindowsPath(windows_config.get("#"))
path_icon = WindowsPath(windows_config.get("#Icon"))
path_lnk = WindowsPath(windows_config.get("#Lnk"))
path_script = WindowsPath(windows_config.get("#Script"))
path_script_txt = WindowsPath(windows_config.get("#ScriptText"))

# 文件夹配置
folders = []
scripts = []


@dataclass
class Desktop:
    name: str = ""
    info: str = ""
    icon: WindowsPath = None
    _ignore_ = False

    def __init__(self, data=None):
        if data == "Ignore":
            self._ignore_ = True
            return
        data = {} if data is None else data
        self.name = data.get("Name") or ""
        self.info = data.get("Info") or ""
        self.icon = data.get("Icon") or ""


@dataclass
class Lnk:
    name: str = ""
    target_path: WindowsPath = WindowsPath()
    working_directory: WindowsPath = WindowsPath()
    description: str = ""
    icon_location: WindowsPath = WindowsPath()
    _ignore_ = False

    def __init__(self, data: dict = None):
        if data == "Ignore":
            self._ignore_ = True
            return
        data = {} if data is None else data
        self.name = data.get("Name") or ""
        self.target_path = data.get("TargetPath") or ""
        self.working_directory = data.get("WorkingDirectory") or ""
        self.description = data.get("Description") or ""
        self.icon_location = data.get("IconLocation") or ""


@dataclass
class Folder:
    path: WindowsPath = WindowsPath()
    desktop: Desktop | None = Desktop()
    lnk: Lnk | None = Lnk()


@dataclass
class Script:
    path: WindowsPath = None
    exe: WindowsPath = None
    args: list = None
    before: list = None
    after: list = None


def check():
    assert windows_config_path
    assert windows_config
    assert path_icon
    assert path_lnk


def init_folders():
    def get_icon(folder: Folder):
        desktop = folder.desktop

        icon = None

        if desktop.icon:
            if str(desktop.icon).endswith(".png"):
                png = path_icon / desktop.icon
                ico = png.with_suffix(".ico")
                if not ico.exists() and png.exists():
                    image = Image.open(png)
                    image.save(ico)
                icon = ico
            elif str(desktop.icon).endswith(".ico"):
                icon = path_icon / desktop.icon
            elif str(desktop.icon).endswith(".exe"):
                icon = folder.path / desktop.icon
        else:
            if desktop.info and desktop.info.endswith(".exe"):
                icon_exe = folder.path / desktop.info
                if icon_exe.exists():
                    icon = icon_exe

            icon_exe = folder.path / f"{folder.path.name}.exe"
            if icon_exe.exists():
                icon = icon_exe

            icon_file = path_icon / f"{folder.path.name}.ico"
            if icon_file.exists():
                icon = icon_file

        return icon

    def get_info(folder: Folder):
        info = folder.desktop.info.strip()

        if not info:
            _exe_ = folder.path / f"{folder.path.name}.exe"
            if _exe_.exists():
                info = exe_version(_exe_)
                return info

        if info and info.endswith(".exe"):
            _exe_ = folder.path / info
            info = exe_version(_exe_.as_posix())
            return info

        # 执行指定命名获取的版本
        # cmd | frpc.exe -v | (\d+) | \1
        if info and info.startswith("cmd |"):
            info = info.split("|")
            info = [item.strip() for item in info]
            _cmd = info[1]
            _match = info[2]
            _get = info[3]
            _get = int(_get) if _get.isdigit() else None

            cmd = f"{folder.path}\\{_cmd}"

            result = subprocess.Popen(cmd,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      shell=True)
            result_out = result.stdout.readlines()
            result_err = result.stderr.readlines()
            result = result_out or result_err
            result = [item.decode() for item in result]
            result = "".join(result)

            obj = re.search(_match, result).group(_get)
            return obj

        # 指定文件内容
        # file | .\ventoy\version | ([\d\.]+) | 1
        if info and info.startswith("file |"):
            info = info.split("|")
            info = [item.strip() for item in info]
            _file_path = info[1]
            _match = info[2]
            _get = info[3]

            _file_path = folder.path / _file_path
            _get = int(_get) if _get.isdigit() else None

            with open(_file_path, "r", encoding="utf-8") as file:
                content = file.read().strip()
                obj = re.search(_match, content).group(_get)
            return obj

        return info

    def init():
        for win_disk in windows_config.keys():
            if not win_disk.startswith("$"):
                continue

            _disk = win_disk.replace("$", "")
            _disk = f"{_disk}:\\" if not _disk.endswith(":\\") else _disk
            path_disk = WindowsPath(_disk)

            # if str(path_disk) == "D:\\":
            #     continue

            global_lnk_ignore: bool = windows_config[win_disk].get("(Lnk)") == "Ignore"
            global_desktop_ignore: bool = windows_config[win_disk].get("(Desktop)") == "Ignore"

            for disk_folder in windows_config[win_disk].keys():

                # Global Config
                if str(disk_folder).startswith("(") and str(disk_folder).endswith(")"):
                    continue

                path_folder = path_disk / disk_folder

                if not path_folder.exists():
                    continue

                folder = Folder()
                folder.path = path_folder

                desktop_config = windows_config[win_disk][disk_folder].get('Desktop')
                lnk_config = windows_config[win_disk][disk_folder].get('Lnk')

                desktop = Desktop(desktop_config)

                folder.desktop = desktop

                if global_lnk_ignore or lnk_config == "Ignore":
                    folder.lnk = None
                    folders.append(folder)
                    continue

                # Default:None \ k-v
                if isinstance(lnk_config, (dict, NoneType)):
                    lnk = Lnk(lnk_config)
                    folder.lnk = lnk
                    folders.append(folder)

                # [k-v]
                if isinstance(lnk_config, list):
                    for index, _lnk_config_ in enumerate(lnk_config):
                        lnk = Lnk(_lnk_config_)
                        folder = copy.deepcopy(folder)
                        folder.lnk = lnk
                        folder.desktop._ignore_ = index == 0
                        folders.append(folder)

    def complete():
        # 初始化Desktop|Lnk默认配置
        folder: Folder
        for folder in folders:
            desktop = folder.desktop
            lnk = folder.lnk

            # if not desktop._ignore_:
            desktop.name = desktop.name or folder.path.name
            desktop.icon = get_icon(folder)
            desktop.info = get_info(folder)

            if not lnk:
                continue

            # if not lnk._ignore_:
            lnk.name = lnk.name or f"{folder.path.name}.lnk"
            if lnk.target_path:
                lnk.target_path = folder.path / lnk.target_path
            else:
                lnk.target_path = folder.path / f"{folder.path.name}.exe"
            if lnk.working_directory:
                lnk.working_directory = folder.path / lnk.working_directory
            else:
                lnk.working_directory = folder.path

            lnk.description = lnk.description or desktop.name or folder.path.name

            if lnk.icon_location:
                if str(lnk.icon_location).endswith(".ico"):
                    lnk.icon_location = path_icon / lnk.icon_location
                elif str(lnk.icon_location).endswith(".exe"):
                    lnk.icon_location = folder.path / lnk.icon_location
                else:
                    lnk.icon_location = desktop.icon
            else:
                lnk.icon_location = folder.desktop.icon

    init()

    complete()


def init_scripts():
    for script_sub_folder in windows_config.get("Script").keys():
        for script_name, script_args in windows_config["Script"][script_sub_folder].items():

            script = Script()
            script.path = path_script / script_sub_folder / f"{script_name}.bat"

            if not script_args:
                scripts.append(script)
                continue

            exe = script_args.get("Exe") or ""
            args = script_args.get("Args") or []
            before = script_args.get("Before") or []
            after = script_args.get("After") or []
            args = [args] if not isinstance(args, list) else args
            before = [before] if not isinstance(before, list) else before
            after = [after] if not isinstance(after, list) else after

            script.exe = exe
            script.args = args
            script.before = before
            script.after = after
            scripts.append(script)


def center_panel_text(text, title="", width=99):
    text = Text(text)
    panel = Panel(text, title=title, title_align="center", width=width, border_style="red")
    panel = Align.center(panel)
    console.print(panel)
    console.print()


def create_desktop(folder: Folder):
    desktop = folder.desktop

    if desktop._ignore_:
        return

    desktop_ini_data = "[.ShellClassInfo]"
    if desktop.icon:
        desktop_ini_data += f"\nIconResource = {desktop.icon} , 0"
    if desktop.info:
        desktop_ini_data += f"\nInfoTip = {desktop.info}"
    if desktop.name and desktop.name != folder.path.name:
        desktop_ini_data += f"\nLocalizedResourceName = {folder.path.name} | {desktop.name}"
    desktop_ini_data = desktop_ini_data.strip()

    desktop_ini_path = folder.path / 'desktop.ini'

    content = ""
    if desktop_ini_path.exists():
        file = open(desktop_ini_path, "r", encoding="gbk")
        content = "".join(file.readlines())
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


def create_script():
    text = ""
    script: Script
    for script in scripts:

        if not script.exe:
            continue

        code = "@Echo Off\n\n"
        code += "SetLocal\n\n"

        if script.before:
            for before in script.before:
                code += f"{before}\n"
            code += "\n"

        code += f"Set Exe=\"{script.exe}\"\n"
        if not script.args or len(script.args) == 0:
            code += f"\n%Exe%  %*\n\n"
        elif len(script.args) == 1:
            code += f"Set Arg=\"{script.args[0]}\"\n\n"
            code += f"%Exe%  %Arg%  %*\n\n"
        elif len(script.args) > 1:
            for index, arg in enumerate(script.args, start=1):
                code += f"Set Arg{index}=\"{arg}\"\n"
            cmd = "\n%Exe%"
            for index in range(1, len(script.args) + 1):
                cmd += f"  %Arg{index}%"
            cmd += "  %*\n\n"
            code += cmd

        if script.after:
            for after in script.after:
                code += f"{after}\n"
            code += "\n"

        code += "EndLocal"

        with open(script.path, "w") as file:
            file.write(code)

        args = ' '.join(script.args) if script.args else ""
        text += f"{script.path.stem:>15}  {script.exe} {args} \n"

    text = text.rstrip()
    title = f"{path_script}\\"
    width = 120
    panel = Panel(text, title=title, title_align="center", width=width, border_style="red")
    console.print(Align.center(panel))


def create_script_txt():
    cnt = 0
    text = " "

    script: Script
    for script in scripts:
        name = script.path.stem
        if len(name) < 11:
            if cnt >= 5:
                text += "\n "
                cnt = 0
            text += name.ljust(11)
            cnt += 1
        elif len(name) < 22:
            if cnt > 4:
                text += "\n "
                cnt = 1
            text += name.ljust(22)
            cnt += 2
        elif len(name) < 33:
            if cnt > 3:
                text += "\n "
                cnt = 1
            text += name.ljust(33)
            cnt += 3
    text = text.rstrip()

    with open(path_script_txt, "w") as file:
        file.write(text)

    width = 11 * 5 + 3 * 2
    title = str(path_script_txt)
    panel = Panel(text, title=title, title_align="center", width=width, border_style="red")
    console.print(Align.center(panel))


def create_lnk(folder: Folder):
    lnk = folder.lnk

    if not lnk or lnk._ignore_:
        return

    tmp_vbs_path = path_tmp / "lnk.vbs"

    content = f'Set ws = WScript.CreateObject("WScript.Shell") \n' \
              f'Set lnk = ws.CreateShortcut("{path_lnk / lnk.name}") \n' \
              f'lnk.TargetPath = "{lnk.target_path}" \n' \
              f'lnk.WorkingDirectory = "{lnk.working_directory}\\" \n' \
              f'lnk.Description = "{lnk.description}" \n' \
              f'lnk.IconLocation = "{lnk.icon_location}" \n' \
              f'lnk.Save()'

    with open(tmp_vbs_path, "w", encoding="gbk") as file:
        file.write(content)

    os.system(f"start {tmp_vbs_path}")
    time.sleep(0.1)


def flush(folder: Folder):
    # Error 刷新文件夹图片
    shell.SHChangeNotify(
        shellcon.SHCNE_UPDATEITEM,
        shellcon.SHCNF_PATH,
        bytes(folder.path.as_posix(), 'gbk'),
        None
    )


def main():
    #
    check()

    # help \ folder \ lnk \ script \ all
    args = sys.argv[1:] if len(sys.argv) > 1 else ["all"]
    args = [item.lower() for item in args]

    arg = args[0] if len(args) >= 1 else "all"

    if arg == "help":
        text = ""
        text += "\n[red]All    [/red] : [green]帮助信息 默认[/green]"
        text += "\n[red]Help   [/red] : [green]帮助信息[/green]"
        text += "\n[red]Folder [/red] : [green]文件信息[/green]"
        text += "\n[red]Lnk    [/red] : [green]文件链接[/green]"
        text += "\n[red]Script [/red] : [green]脚本文件[/green]"
        text += "\n"
        console.print(text)
        return

    def create_table():
        table = Table()
        table.add_column("Folder", justify="left", width=30)
        table.add_column("Icon", justify="left", width=35)
        table.add_column("Info", justify="center", width=20)
        table.add_column("Name", justify="center", width=20)
        return table

    if arg in ["folder", "all"]:
        console.clear()
        console.print()

        init_folders()

        table = create_table()
        table_center = Align.center(table)
        with Live(table_center, console=console) as live:
            folder: Folder
            for folder in folders:
                create_desktop(folder)
                flush(folder)
                line = [f"{folder.path}\\",
                        folder.desktop.icon or "",
                        folder.desktop.info or "",
                        folder.desktop.name if folder.desktop.name != folder.path.name else ""]
                line = [str(item) for item in line]
                if folder.desktop._ignore_:
                    continue
                table.add_row(*line)
                if table.row_count > console.height - 6:
                    table.columns.clear()
                    table = create_table()
                    table_center = Align.center(table)
                    live.update(table_center)

        if arg == "folder":
            return

        time.sleep(3)
        console.clear()

    if arg in ["lnk", "all"]:
        lnks = []
        init_folders()
        folder: Folder
        for folder in folders:
            if folder.lnk:
                create_lnk(folder)
                if name := folder.lnk.name:
                    lnks.append(name)

        lnks.sort()
        text = ""
        for index, item in enumerate(lnks, start=1):
            text += f"{item:<20}"
            if index % 5 == 0:
                text += "\n"

        panel = Panel(text, title=f"{path_lnk}\\", title_align="center", width=120,
                      border_style="red")
        console.print()
        console.print()
        console.print(Align.center(panel))

        if arg == "lnk":
            return

        time.sleep(1.5)
        console.clear()

    if arg in ["all", "script"]:
        init_scripts()
        console.print()
        console.print()
        create_script()
        console.print()
        create_script_txt()
        if arg == "script":
            return
        time.sleep(1.5)
        console.clear()


def test():
    pass
    init_folders()
    print(folders)

    # init_scripts()
    # print(scripts)

    # create_script()
    # create_script_txt()


if __name__ == '__main__':
    # test()
    main()
