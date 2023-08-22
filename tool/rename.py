import os
import sys
import win32api
import logging
import inspect
from collections.abc import Callable
from typing import List, Any
from pathlib import Path, WindowsPath

from rich import print
from rich import box
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.markup import escape
from rich.table import Table
from hanziconv import HanziConv

_print_ = print


class File(object):
    def __init__(self):
        self.old: WindowsPath = WindowsPath()
        self.new: WindowsPath = WindowsPath()
        self.rule: Any = ""

    def __str__(self):
        return f"{self.old.name}\t-> {self.new.name} | {self.rule}"


class Rename(object):
    def __init__(self):
        self.folder: WindowsPath = WindowsPath()  # 重命名文件夹目录
        self.files: List[File] = []  # 需要重命名的文件 新名字-旧名字
        self.rule: Callable([WindowsPath], WindowsPath) = lambda x: x  # 匹配 重命名 规则
        self.duplicate: List[File] = []  # 重复的文件

    def __bool__(self):
        return bool(len(self.files))

    def init(self):
        for path_file in self.folder.iterdir():
            if path_file.is_dir():
                continue
            result = self.rule(path_file)
            if not result:
                continue

            new_name, rule = result

            path_file_old = path_file
            path_file_new = new_name

            file = File()
            file.old = path_file_old
            file.new = path_file_new
            file.rule = rule
            file.new = change_name(file.new)
            if file.old == file.new:
                continue
            self.files.append(file)
        try:
            self.sort()
        except Exception as e:
            print(e)

    def sort(self):

        def key(item: File):
            # _name_, _type_ = os.path.splitext(item.new)
            # _name_ = int(_name_) if _name_.isdigit() else _name_
            # return _name_
            return item.new.name

        self.files = sorted(self.files, key=key)

    def debug(self):
        _print_()
        for item in self.files:
            _print_(f"  {item}")
        _print_()

    def config(self):
        rule = inspect.getsource(self.rule)
        print()
        print(Syntax(rule, "python3", line_numbers=True, indent_guides=True))
        print()

    def command(self, arg):
        if arg == "help":
            print()
            print("help")
            print("debug")
            print("config")
            print()
            exit()
        if arg == "debug":
            self.debug()
            exit()
        if arg == "config":
            self.config()
            exit()

    def start(self, silent=False):
        if not self:
            return

        rename_index = []

        if silent:
            check = "\\"
        else:
            check = Prompt.ask('[red]确认重命名[/red]')

        if not check:
            print("\n[red]取消重命名[/red]\n")
            return

        if check.isdigit():
            rename_index = [check]
            check = '\\'

        if ',' in check or '`' in check or ' ' in check:
            check = check.replace(',', ' ')
            check = check.replace('`', ' ')
            rename_index = check.split()
            check = '\\'

        rename_index = [int(obj) for obj in rename_index]

        if check:
            if check not in ['\\']:
                print("\n[red]取消重命名[/red]\n")
                return

            if check in ['\\\\']:
                print("\n[red]取消重命名[/red]\n")
                return

        if not silent:
            print("\n[red]开始重命名[/red]", end="///")

        for index, file in enumerate(self.files, 1):
            if not rename_index:
                try:
                    file.old.rename(file.new)
                except FileExistsError:
                    self.duplicate.append(file)
                    continue
            elif index in rename_index:
                try:
                    file.old.rename(file.new)
                except FileExistsError:
                    self.duplicate.append(file)
                    continue
        if not silent:
            print("[red]结束重命名[/red]\n")

    def remove_duplicate(self):
        self.files = self.duplicate
        self.print(title="Duplicate Files")

        check = Prompt.ask('[red]是否删除重复文件[/red]')
        if not check or check != "\\":
            print("\n[red]取消删除[/red]\n")
            return
        elif check == "\\":
            print("\n[red]开始删除[/red]", end="///")
            for file in self.files:
                file.old.unlink()
            print("[red]结束删除[/red]\n")

    def print(self, title=""):
        if not self:
            print()
            print("[red]  [ No Rename ]  [/red]")
            print()
            return
        print()
        table = Table(box=box.ROUNDED)
        table.title = title
        table.add_column("Old", justify="center")
        table.add_column("I*", justify="center")
        table.add_column("New", justify="center")
        for index, file in enumerate(self.files, 1):
            _old_ = escape(file.old.name)
            _new_ = escape(file.new.name)
            table.add_row(_old_, f"<{str(index).zfill(2)}>", _new_)
        print(table)
        print()


def get_version(file: WindowsPath | str):
    if isinstance(file, WindowsPath):
        file = file.as_posix()
    try:
        info = win32api.GetFileVersionInfo(file, os.sep)
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        high = win32api.HIWORD
        low = win32api.LOWORD
        result = f"{high(ms)}.{low(ms)}.{high(ls)}.{low(ls)}"
        return result
    except Exception as e:
        logging.exception(e)
        return None


def change_name(file: WindowsPath | str) -> WindowsPath | str:
    """ 简繁转换 替换不支持的特殊符号 """
    if not file:
        return file

    new_name = file

    if isinstance(file, WindowsPath):
        new_name = file.name
    elif isinstance(file, str):
        new_name = file

    codes = [
        ('?', '？'),
        (',', '，'),

        (':', '-'),

        ('<', '['),
        ('>', ']'),
        ('【', '['),
        ('】', ']'),

        ('\\', ''),
        ('/', ''),
        ('|', ''),
        ('*', ''),
    ]
    for item in codes:
        new_name = new_name.replace(item[0], item[1])
    try:
        new_name = HanziConv.toSimplified(new_name)
    except ImportError:
        pass
    finally:
        if isinstance(file, WindowsPath):
            file = file.with_name(new_name)
            return file
        elif isinstance(file, str):
            return new_name
        return file