import re
import os
import sys
import copy
import types
import typing
import win32api
import logging
import inspect

from collections.abc import Callable
from typing import List, Any
from pathlib import Path, WindowsPath
from functools import partial
from inspect import isfunction

from rich import print
from rich import box
from rich.align import Align
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.markup import escape
from rich.table import Table
from hanziconv import HanziConv

from .tool import change_name

_print_ = print


class File(object):
    def __init__(self):
        self.old: WindowsPath = WindowsPath()
        self.new: WindowsPath = WindowsPath()
        self.rule: Any = ""

    def __str__(self):
        if isinstance(self.rule, types.FunctionType):
            name = self.rule.__qualname__
        return f"{self.old.name}\t-> {self.new.name} | {self.rule}"


class Rename(object):
    def __init__(self):
        self.folder: WindowsPath = WindowsPath()  # 重命名文件夹目录
        self.config: List[List] = []  # 重命名规则
        self.files: List[File] = []  # 需要重命名的文件 新名字-旧名字
        self.duplicate: List[File] = []  # 重复的文件

    def __bool__(self):
        return bool(len(self.files))

    def rule(self, file: WindowsPath):
        """ 重命名函数
        @param file: 需要重命名文件的完整路径
        @return: 重命名文件名 | 命名规则
        """
        for cfg in self.config:
            if isfunction(cfg) or isinstance(cfg, partial):
                fun = cfg
                try:
                    result = fun(file)
                except Exception as e:
                    continue
                if result and isfunction(cfg):
                    return result, f"<F> {fun.__name__}"
                if result and isinstance(cfg, partial):
                    return result, f"<F> {fun.func.__name__}"
                continue

            _match_, _get_ = cfg[0], cfg[1]

            if not isinstance(_match_, str):
                continue

            if not re.match(_match_, file.name):
                continue

            if isinstance(_get_, str):
                new_name = re.sub(_match_, _get_, file.name)
                file = file.with_name(new_name)
                return file, f"{_match_} / {_get_}"

            if isfunction(_get_) or isinstance(_get_, partial):
                file = _get_(file)
                info = ""
                if isinstance(_get_, partial):
                    info = f"<F> {_get_.func.__name__}"
                if isfunction(_get_):
                    info = f"<F> {_get_.__name__}"
                return file, f"{_match_} / {info}"

            if isinstance(_get_, (list, tuple)):
                info = ""
                for _g_ in _get_:
                    if isinstance(_g_, str):
                        new_name = re.sub(_match_, _g_, file.name)
                        file = file.with_name(new_name)
                        info = info + _g_ + " & "
                    elif isfunction(_g_) or isinstance(_g_, partial):
                        file = _g_(file)
                        if isinstance(_g_, partial):
                            info = info + f"<F> {_g_.func.__name__}"
                        if isfunction(_g_):
                            info = info + f"<F> {_g_.__name__}"
                return file, f"{_match_} / {info}"

    def init(self):
        for path_file in self.folder.iterdir():
            if path_file.is_dir():
                continue
            result = self.rule(path_file)
            if not result:
                continue

            new_name, rename_rule = result

            path_file_old = path_file
            path_file_new = new_name

            file = File()
            file.old = path_file_old
            file.new = path_file_new
            file.rule = rename_rule
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

    def remove_duplicate(self, silent=False):
        self.files = self.duplicate
        self.print(title="Duplicate Files")

        if silent:
            for file in self.files:
                file.old.unlink()
            return

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
            print(f"[red]  [ No Rename ]  [/red] {self.folder}\\")
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
            table.add_row(Align(_old_), f"<{str(index).zfill(2)}>", Align(_new_))
        print(table)
        print()

    # def config(self):
    #     rule = inspect.getsource(self.rule)
    #     print()
    #     print(Syntax(rule, "python3", line_numbers=True, indent_guides=True))
    #     print()