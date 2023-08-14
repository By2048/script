# [2022-01-12]
import re
import os
import sys
import hashlib
import shutil
import time
import copy
from types import NoneType
from typing import List, Dict

import yaml
import ctypes
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


def yaml_join(loader, node):
    nodes = loader.construct_sequence(node)
    return ' '.join([item for item in nodes])


yaml.add_constructor(r'!Join', yaml_join)

console = get_console()

windows_config_folder = WindowsPath('E:\\Config\\Windows\\')

windows_config: dict = {}

for config_file in windows_config_folder.iterdir():
    with open(config_file, encoding="utf-8") as file:
        config_item: dict = yaml.unsafe_load(file)
        for key, value in config_item.items():
            if key not in windows_config.keys():
                windows_config[key] = value
            else:
                windows_config[key] |= value

path_tmp = WindowsPath(windows_config.get("#"))
path_icon = WindowsPath(windows_config.get("#Icon"))
path_lnk = WindowsPath(windows_config.get("#Lnk"))
path_script = WindowsPath(windows_config.get("#Script"))
path_script_txt = WindowsPath(windows_config.get("#ScriptText"))


@dataclass
class Desktop:
    name: str = ""
    info: str | list = ""
    icon: WindowsPath = None
    rename: Dict = None

    def __bool__(self):
        return bool(self.name) or bool(self.info) or bool(self.icon)

    def __init__(self, data=None):
        data = {} if data is None else data
        self.name = data.get("Name") or ""
        self.info = data.get("Info") or ""
        self.icon = data.get("Icon") or ""
        self.rename = data.get("Rename") or ""


@dataclass
class Lnk:
    name: str = ""
    target_path: WindowsPath = WindowsPath()
    working_directory: WindowsPath = WindowsPath()
    description: str = ""
    icon_location: WindowsPath = WindowsPath()

    def __bool__(self):
        return bool(self.name) or bool(self.target_path)

    def __init__(self, data: dict = None):
        data = {} if data is None else data
        self.name = data.get("Name") or ""
        self.target_path = data.get("TargetPath") or ""
        self.working_directory = data.get("WorkingDirectory") or ""
        self.description = data.get("Description") or ""
        self.icon_location = data.get("IconLocation") or ""


@dataclass
class Folder:
    path: WindowsPath = WindowsPath()
    desktop: Desktop = Desktop()
    lnks: List[Lnk] = None  # noqa

    def __repr__(self):
        data = f">folder  {self.path}"
        if self.desktop:
            data = data + "\n desktop "
            data = data + f"{self.desktop.name} {self.desktop.icon} {self.desktop.info}"
        if self.lnks:
            for lnk in self.lnks:
                data = data + "\n lnk     "
                data = data + f"{lnk.name} {lnk.target_path} {lnk.working_directory}"
        return data


@dataclass
class Script:
    type: str = "Bat"  # Bat Or PowerShell
    path: WindowsPath = None
    exe: WindowsPath = None
    args: list = None
    before: list = None
    after: list = None
    commands: list = None

    def __repr__(self):
        return self.exe

    def __bool__(self):
        return bool(self.exe)


# 文件夹配置
folders: List[Folder] = []
scripts: List[Script] = []


def check():
    assert windows_config_folder
    assert windows_config
    assert path_icon
    assert path_lnk


def init_folders():
    def get_icon(folder: Folder):
        desktop = folder.desktop

        icon = None

        # 默认位置寻找图标并支持png转ico
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

        # 使用软件中默认的图标
        if desktop.icon and ".exe" in desktop.icon:
            icon = folder.path / desktop.icon
            return icon

        # 在相对位置和默认位置寻找图标
        if desktop.icon and ".ico" in desktop.icon:
            icon = folder.path / desktop.icon
            if icon.exists():
                return icon

        # 使用文件夹对应的默认图标
        ico_file = path_icon / f"{folder.path.name}.ico"
        if ico_file.exists():
            return ico_file
        png_file = path_icon / f"{folder.path.name}.png"
        if png_file.exists() and not ico_file.exists():
            image = Image.open(png_file)
            image.save(ico_file)
            return ico_file

        return icon

    def get_info(folder: Folder):
        info = folder.desktop.info

        # 尝试使用默认配置进行解析
        if not info:
            _exe_ = folder.path / f"{folder.path.name}.exe"
            if _exe_.exists():
                version = exe_version(_exe_)
                return version

        all_info = []
        if isinstance(info, str):
            all_info = [info.strip()]
        if isinstance(info, list):
            all_info = [item.strip() for item in info]

        info_content = []

        for info in all_info:

            # 软件版本信息
            if info.lower().endswith(".exe"):
                _exe_ = folder.path / info
                version = exe_version(_exe_.as_posix())
                if version:
                    info_content.append(version)
                continue

            # 执行指定命名获取的版本
            # cmd | frpc.exe -v | (\d+) | \1
            if info.lower().startswith("cmd |"):
                _info = info.split("|")
                _info = [item.strip() for item in _info]
                _cmd = _info[1]
                _cmd = _cmd.lstrip(".\\")
                _match = _info[2]
                _get = _info[3]
                _get = int(_get) if _get.isdigit() else None

                cmd = f"{folder.path}\\{_cmd}"
                result = subprocess.Popen(cmd,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          shell=True)
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
                    info_content.append(obj)
                continue

            # 指定文件内容
            # file | .\ventoy\version | ([\d\.]+) | 1
            if info.lower().startswith("file |"):
                _info = info.split("|")
                _info = [item.strip() for item in _info]
                _file_path = _info[1]
                _match = _info[2]
                _get = _info[3]

                _file_path = folder.path / _file_path
                _get = int(_get) if _get.isdigit() else None

                with open(_file_path, "r", encoding="utf-8") as file:
                    content = file.read().strip()
                    obj = re.search(_match, content).group(_get)
                if obj:
                    info_content.append(obj)
                continue

            # 文件数量
            if info.lower().startswith("count | *"):
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
                info_content.append(total)
                continue

            if info:
                info_content.append(info)

        return " | ".join(info_content) if info_content else ""

    def get_rename(folder: Folder):
        info = {}
        rename = folder.desktop.rename
        if not rename:
            return info
        if isinstance(rename, str):
            rename = [rename]
        for item in rename:
            items = item.split("|")
            key = items[0].rstrip()
            value = items[1].lstrip()
            info[key] = value
        return info

    def init():
        for win_disk in windows_config.keys():
            if not win_disk.startswith("$"):
                continue

            disk = win_disk.replace("$", "")
            disk_path = WindowsPath(disk)

            for disk_folder in windows_config[win_disk].keys():
                path_folder = disk_path / disk_folder
                if not path_folder.exists():
                    continue

                desktop_config = windows_config[win_disk][disk_folder].get('Desktop')
                lnk_config = windows_config[win_disk][disk_folder].get('Lnk')

                folder = Folder()
                folder.path = path_folder
                desktop = Desktop(desktop_config)
                folder.desktop = desktop

                if not lnk_config:
                    folder.lnks = []

                # Default:None \ k-v 一个快捷方式
                if lnk_config and isinstance(lnk_config, dict):
                    folder.lnks = [Lnk(lnk_config)]

                # [k-v] 多个快捷方式
                if lnk_config and isinstance(lnk_config, list):
                    folder.lnks = [Lnk(item) for item in lnk_config]

                folders.append(folder)

    def complete_desktop():
        # 初始化Desktop|Lnk默认配置
        folder: Folder
        for folder in folders:
            folder.desktop.name = folder.desktop.name or folder.path.name
            folder.desktop.icon = get_icon(folder)
            folder.desktop.info = get_info(folder)
            folder.desktop.rename = get_rename(folder)

    def complete_lnks():
        folder: Folder
        for folder in folders:
            lnk_default_exe = folder.path / f"{folder.path.name}.exe"
            if not folder.lnks and lnk_default_exe.exists():
                lnk = Lnk()
                lnk.name = f"{folder.path.name}.lnk"
                lnk.target_path = folder.path / f"{folder.path.name}.exe"
                lnk.working_directory = folder.path
                lnk.description = folder.path.name
                lnk.icon_location = folder.desktop.icon
                folder.lnks = [lnk]
                continue

            for lnk in folder.lnks:
                if not lnk and not lnk_default_exe.exists():
                    continue

                lnk.name = lnk.name or f"{folder.path.name}.lnk"
                if not lnk.name.endswith(".lnk"):
                    lnk.name = f"{lnk.name}.lnk"
                if lnk.target_path:
                    lnk.target_path = folder.path / lnk.target_path
                else:
                    lnk.target_path = folder.path / f"{folder.path.name}.exe"
                if lnk.working_directory:
                    lnk.working_directory = folder.path / lnk.working_directory
                else:
                    lnk.working_directory = folder.path

                lnk.description = lnk.description or folder.desktop.name or folder.path.name

                if lnk.icon_location:
                    if str(lnk.icon_location).endswith(".ico"):
                        lnk.icon_location = path_icon / lnk.icon_location
                    elif str(lnk.icon_location).endswith(".exe"):
                        lnk.icon_location = folder.path / lnk.icon_location
                    else:
                        lnk.icon_location = folder.desktop.icon
                else:
                    lnk.icon_location = folder.desktop.icon

    if not folders:
        init()
        complete_desktop()
        complete_lnks()


def init_scripts():
    for script_sub_folder in windows_config.get("Script").keys():
        config_items = windows_config["Script"][script_sub_folder].items()
        for script_name, script_args in config_items:
            script = Script()

            if not script_args:
                scripts.append(script)
                continue

            exe = script_args.get("Exe") or ""
            args = script_args.get("Args") or []
            before = script_args.get("Before") or []
            after = script_args.get("After") or []
            commands = script_args.get("Commands") or []
            args = [args] if not isinstance(args, list) else args
            before = [before] if not isinstance(before, list) else before
            after = [after] if not isinstance(after, list) else after
            commands = [commands] if not isinstance(commands, list) else commands

            script.exe = exe
            script.args = args
            script.before = before
            script.after = after
            script.commands = commands
            script.type = script_args.get("Type") or "Bat"
            if script.type == "Bat":
                script.path = path_script / script_sub_folder / f"{script_name}.bat"
            if script.type == "PowerShell":
                script.path = path_script / script_sub_folder / f"{script_name}.ps1"
            if script:
                scripts.append(script)


def center_panel_text(text, title="", width=99):
    text = Text(text)
    panel = Panel(text, title=title, title_align="center",
                  width=width, border_style="red")
    panel = Align.center(panel)
    console.print(panel)
    console.print()


def create_desktop(folder: Folder):
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
    finally:
        os.system(f" attrib +r \"{folder.path.as_posix()}\" ")


def create_script():
    def create_script_bat():
        code = "@Echo Off\n\n"
        code += "SetLocal\n\n"

        if script.before:
            for before in script.before:
                code += f"{before}\n"
            code += "\n"

        if script.exe:
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

        if script.commands:
            code += "\n"
            for command in script.commands:
                code = code + command + "\n\n"
            code += "\n"

        code += "EndLocal"

        with open(script.path, "w") as file:
            file.write(code)

    def create_script_psl():
        code = ""

        if script.before:
            for before in script.before:
                code += f"{before}\n"
            code += "\n"

        if script.exe:
            code += f"$Exe = \"{script.exe}\"\n\n"
            if not script.args or len(script.args) == 0:
                code += f"&  $Exe  $Args"
            elif len(script.args) == 1:
                code += f"$Arg=\"{script.args[0]}\"\n\n"
                code += f"&  $Exe  $Arg"
            elif len(script.args) > 1:
                for index, arg in enumerate(script.args, start=1):
                    code += f"$Arg{index}=\"{arg}\"\n"
                cmd = "\n&  $Exe"
                for index in range(1, len(script.args) + 1):
                    cmd += f"  $Arg{index}   $Args"
                code += cmd

        if script.after:
            for after in script.after:
                code += f"{after}\n"
            code += "\n"

        if script.commands:
            code += "\n"
            for command in script.commands:
                code = code + command + "\n\n"
            code += "\n"

        with open(script.path, "w") as file:
            file.write(code)

    text = ""
    script: Script
    for script in scripts:
        if not script.exe and not script.commands:
            continue

        if script.type == "Bat":
            create_script_bat()
        if script.type == "PowerShell":
            create_script_psl()

        args = ' '.join(script.args) if script.args else ""
        text += f"{script.path.stem:>15}  {script.exe} {args} \n"

    text = text.rstrip()
    title = f"{path_script}\\"
    width = 120
    panel = Panel(text, title=title, title_align="center",
                  width=width, border_style="red")
    console.print(Align.center(panel))


def create_script_txt():
    cnt = 0
    text = " "

    script: Script
    for script in scripts:
        if not script:
            continue
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
    panel = Panel(text, title=title, title_align="center",
                  width=width, border_style="red")
    console.print(Align.center(panel))


def create_lnk(lnk: Lnk):
    if not lnk:
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


def flush():
    # 刷新文件夹图片
    ctypes.windll.shell32.SHChangeNotify(
        shellcon.SHCNE_ASSOCCHANGED,
        shellcon.SHCNF_IDLIST,
        0,
        0
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
                line = [f"{folder.path}\\",
                        folder.desktop.icon or "",
                        folder.desktop.info or "",
                        folder.desktop.name if folder.desktop.name != folder.path.name else ""]
                line = [str(item) for item in line]
                if not folder.desktop:
                    continue
                table.add_row(*line)
                if table.row_count > console.height - 6:
                    table.columns.clear()
                    table = create_table()
                    table_center = Align.center(table)
                    live.update(table_center)

        flush()

        if arg == "folder":
            return

        time.sleep(3)
        console.clear()

    if arg in ["lnk", "all"]:
        lnks_name = []
        init_folders()
        for folder in folders:
            if not folder.lnks:
                continue
            for lnk in folder.lnks:
                if not lnk:
                    continue
                create_lnk(lnk)
                lnks_name.append(lnk.name.rstrip(".lnk"))

        lnks_name.sort()
        text = ""
        for index, item in enumerate(lnks_name, start=1):
            text += f"{item:<20}"
            if index % 5 == 0:
                text += "\n"

        panel = Panel(text, title=f"{path_lnk}\\", title_align="center",
                      width=120, border_style="red")
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
    # init_folders()
    # print(folders)

    # for folder in folders:
    #     create_desktop(folder)

    # init_scripts()
    # print(scripts)

    # create_script()
    # create_script_txt()
    pass


if __name__ == '__main__':
    # test()
    main()