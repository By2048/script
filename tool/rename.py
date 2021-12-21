import os
import sys
from collections.abc import Callable

import win32api
import inspect
import copy
from typing import List
from pathlib import Path, WindowsPath

_print_ = print

from rich import print
from rich import box
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.markup import escape
from rich.table import Table
from hanziconv import HanziConv


class File(object):
    def __init__(self):
        self.old: WindowsPath = WindowsPath()
        self.new: WindowsPath = WindowsPath()

    def __str__(self):
        return f"{self.old.name} -> {self.new.name}"


class Rename(object):
    def __init__(self):
        self.folder: WindowsPath = WindowsPath()  # 重命名文件夹目录
        self.files: List[File] = []  # 需要重命名的文件 新名字-旧名字
        self.rule: Callable([WindowsPath], WindowsPath) = lambda x: x  # 匹配 重命名 规则

    def __bool__(self):
        return bool(len(self.files))

    def init(self):
        for path_file in self.folder.iterdir():
            if path_file.is_dir():
                continue
            result = self.rule(path_file)
            if not result:
                continue

            path_file_old = path_file
            path_file_new = result

            file = File()
            file.old = path_file_old
            file.new = path_file_new
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
        _print_(self.folder)
        for item in self.files:
            _print_(f"    {item}")
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

            # old = os.path.join(self.folder, file.old)
            # new = os.path.join(self.folder, file.new)

            if not rename_index:
                file.old.rename(file.new)
                # os.rename(old, new)
                continue
            if index in rename_index:
                file.old.rename(file.new)
                # os.rename(old, new)
                continue
        if not silent:
            print("[red]结束重命名[/red]\n")

    def print(self):
        if not self:
            print()
            print("[red][No Rename][/red]")
            print()
            return
        print()
        table = Table(box=box.ROUNDED)
        table.add_column("old_name", justify="right")
        table.add_column("I", justify="center")
        table.add_column("new_name", justify="left")
        for index, file in enumerate(self.files, 1):
            _old_ = escape(file.old.name)
            _new_ = escape(file.new.name)
            table.add_row(_old_, str(index), _new_)
        print(table)
        print()


def get_version(file: WindowsPath):
    try:
        info = win32api.GetFileVersionInfo(file, os.sep)
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        high = win32api.HIWORD
        low = win32api.LOWORD
        result = f"{high(ms)}.{low(ms)}.{high(ls)}.{low(ls)}"
        return result
    except Exception as e:
        print(e)
        return None


def change_name(file: WindowsPath) -> WindowsPath:
    """ 简繁转换 替换不支持的特殊符号 """
    if not file:
        return file

    new_name = file.name

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
        file = file.with_name(new_name)
        return file
