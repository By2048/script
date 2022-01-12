# [2022-01-12]
import re
import os
import sys
import hashlib
import shutil
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

try:
    from tool.file import lnk_to_exe, version
except ImportError:
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(path)
    from tool.file import lnk_to_exe, exe_version

windows_config_path = WindowsPath('E:\\Config\\Windows.yaml')
assert windows_config_path

windows_config: dict
with open(windows_config_path, encoding="utf-8") as file:
    windows_config = yaml.unsafe_load(file)
assert windows_config

path_icon = WindowsPath(windows_config.get("#Icon"))
path_lnk = WindowsPath(windows_config.get("#Lnk"))
assert path_icon
assert path_lnk

path_script = WindowsPath(windows_config.get("#Script"))
path_script_txt = WindowsPath(windows_config.get("#ScriptText"))

path_tmp = WindowsPath(windows_config.get("#"))

# 文件夹配置
folders = []
scripts = []

console = get_console()


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
        # self.icon = WindowsPath(self.icon) if self.icon else None


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
        # formatter:off
        # self.target_path = WindowsPath(self.target_path) if self.target_path else None
        # self.working_directory = WindowsPath(self.working_directory) if self.working_directory else None
        # self.icon_location = WindowsPath(self.icon_location) if self.icon_location else None
        # formatter:on

    def __bool__(self):
        return bool(self.name) and bool(self.target_path)


@dataclass
class Folder:
    path: WindowsPath = WindowsPath()
    desktop: Desktop = Desktop()
    lnk: Lnk = Lnk()


@dataclass
class Script:
    path: WindowsPath = None
    exe: WindowsPath = None
    args: str = None


def init_folders():
    # 获取软件图标
    def get_icon(folder: Folder):

        if not folder.desktop.icon:
            icon = path_icon / f"{path_folder.name}.ico"
        else:
            icon = path_icon / folder.desktop.icon

        if icon.exists():
            return icon

        return

    # 获取软件信息
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

            result = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            result = result.stdout.readlines()
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

    for win_disk in windows_config.keys():
        if not win_disk.startswith("$"):
            continue

        _disk = win_disk.replace("$", "")
        _disk = f"{_disk}:\\" if not _disk.endswith(":\\") else _disk
        path_disk = WindowsPath(_disk)

        for disk_folder in windows_config[win_disk].keys():
            path_folder = path_disk / WindowsPath(disk_folder)

            if not path_folder.exists():
                continue

            desktop_config = windows_config[win_disk][disk_folder].get('Desktop')

            lnk_config = windows_config[win_disk][disk_folder].get('Lnk')
            if isinstance(lnk_config, list):
                index = 0
                for _lnk_config_ in lnk_config:
                    folder = Folder()
                    lnk = Lnk(_lnk_config_)
                    desktop = Desktop(desktop_config)
                    desktop._ignore_ = False if index == 0 else True
                    folder.path = path_folder
                    folder.desktop = desktop
                    folder.lnk = lnk
                    index += 1
                    folders.append(folder)
            else:
                folder = Folder()
                lnk = Lnk(lnk_config)
                desktop = Desktop(desktop_config)
                folder.path = path_folder
                folder.desktop = desktop
                folder.lnk = lnk
                folders.append(folder)

        del disk_folder

        # 初始化Desktop|Lnk默认配置
        folder: Folder
        for folder in folders:
            path_folder = folder.path
            desktop = folder.desktop
            lnk = folder.lnk

            desktop.name = desktop.name or path_folder.name
            desktop.icon = get_icon(folder)
            desktop.info = get_info(folder)

            if lnk._ignore_:
                continue

            lnk.name = lnk.name or f"{path_folder.name}.lnk"
            lnk.name = f"{lnk.name}.lnk" if not lnk.name.endswith(".lnk") else lnk.name
            lnk.target_path = lnk.target_path or f"{path_folder.name}.exe"
            lnk.target_path = folder.path / lnk.target_path
            lnk.working_directory = folder.path / lnk.working_directory or path_folder
            lnk.description = lnk.description or desktop.name or ""
            lnk.icon_location = desktop.icon or path_icon / lnk.target_path


def init_scripts():
    for script_sub_folder in windows_config.get("Script").keys():
        for script_name, script_args in windows_config["Script"][script_sub_folder].items():
            args = script_args
            args = [] if args is None else args
            args = [args] if isinstance(args, str) else args
            args = [arg for arg in args if arg is not None]
            script = Script()
            script.path = path_script / script_sub_folder / f"{script_name}.bat"
            if args:
                script.exe = args[0]
                script.args = args[1:] if len(args) > 1 else []
            scripts.append(script)


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
    os.system(f" attrib -s -h \"{desktop_ini_path}\" ")

    try:
        with open(desktop_ini_path, 'w', encoding="gbk") as file:
            file.write(desktop_ini_data)
    except Exception as e:
        logger.exception(e)

    os.system(f" attrib +s +h \"{desktop_ini_path}\" ")


def create_script():
    result = ""
    script: Script
    for script in scripts:
        exe = script.exe
        args = script.args

        if not exe:
            continue

        content = "@Echo Off\n\n"
        content += "SetLocal\n\n"
        content += f"Set Exe=\"{exe}\"\n"

        if not args or len(args) == 0:
            content += f"\n%Exe%  %*\n\n"
        elif len(args) == 1:
            content += f"Set Arg=\"{args[0]}\"\n\n"
            content += f"%Exe%  %Arg%  %*\n\n"
        elif len(args) > 1:
            for index, arg in enumerate(args, start=1):
                content += f"Set Arg{index}=\"{arg}\"\n"
            cmd = "\n%Exe%"
            for index in range(1, len(args) + 1):
                cmd += f"  %Arg{index}%"
            cmd += "  %*\n\n"
            content += cmd

        content += "EndLocal"

        with open(script.path, "w") as file:
            file.write(content)

        if not exe:
            continue

        args = ' '.join(args) if args else ""
        result += f"{script.path.stem:>15}  {exe} {args} \n"

    result = result.rstrip()

    txt = Text(result)

    width = 120

    panel = Panel(txt, title=f"{path_script}\\", title_align="center",
                  width=width, border_style="red")

    left = (console.width - width) / 2
    left = int(left)
    padding = Padding(panel, (0, 0, 0, left))

    console.print(padding)


def create_script_txt():
    txt = " "
    script: Script
    cnt = 0
    for script in scripts:
        name = script.path.stem

        if len(name) < 11:
            if cnt >= 5:
                txt += "\n "
                cnt = 0
            txt += name.ljust(11)
            cnt += 1
        elif len(name) < 22:
            if cnt > 4:
                txt += "\n "
                cnt = 1
            txt += name.ljust(22)
            cnt += 2
        elif len(name) < 33:
            if cnt > 3:
                txt += "\n "
                cnt = 1
            txt += name.ljust(33)
            cnt += 3

    txt = txt.rstrip()

    with open(path_script_txt, "w") as file:
        file.write(txt)

    txt = Text(txt)

    width = 11 * 5 + 3 + 3

    panel = Panel(txt,
                  title=str(path_script_txt),
                  title_align="center",
                  width=width, border_style="red")

    left = (console.width - width) / 2
    left = int(left)
    padding = Padding(panel, (0, 0, 0, left))

    console.print(padding)
    console.print()


def create_lnk(folder: Folder):
    lnk = folder.lnk

    if lnk._ignore_:
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
    init_folders()
    init_scripts()

    table = Table()
    table.add_column("Folder", justify="left", width=30)
    table.add_column("Icon", justify="left", width=35)
    table.add_column("Info", justify="center", width=20)
    table.add_column("Name", justify="center", width=20)
    table_center = Align.center(table)

    console.clear()
    console.print()

    with Live(table_center, console=console, refresh_per_second=30):
        folder: Folder
        for folder in folders:
            create_desktop(folder)
            create_lnk(folder)
            flush(folder)
            line = [f"{folder.path}\\",
                    folder.desktop.icon or "",
                    folder.desktop.info or "",
                    folder.desktop.name if folder.desktop.name != folder.path.name else ""]
            line = [str(item) for item in line]
            if folder.desktop._ignore_:
                continue
            table.add_row(*line)
            # continue

    console.print()
    console.print()

    create_script()
    console.print()
    console.print()

    create_script_txt()
    console.print()
    console.print()


def test():
    init_folders()
    print(folders)

    init_scripts()
    print(scripts)


if __name__ == '__main__':
    # test()
    main()
