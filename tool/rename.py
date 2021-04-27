import os
import sys
import inspect
from typing import List

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
        self.old_name = ""
        self.new_name = ""
        self.rename_rule = ""

    def __str__(self):
        return f"{self.old_name:<35} | {self.new_name:<35} | {self.rename_rule}"


class Rename(object):
    def __init__(self):
        self.folder: str = ""  # 重命名文件夹目录
        self.files: List[File] = []  # 需要重命名的文件 新名字-旧名字
        self.rule = None  # 匹配 重命名 规则

    def __bool__(self):
        return bool(len(self.files))

    def init(self):
        for item in os.listdir(self.folder):
            result = self.rule(item)
            if not result:
                continue
            file = File()
            file.old_name = item
            file.new_name = result[0]
            file.rename_rule = result[1]
            file.new_name = change_name(file.new_name)
            self.files.append(file)
        try:
            self.sort()
        except Exception as e:
            print(e)

    def sort(self):

        def key(item: File):
            _name_, _type_ = os.path.splitext(item.new_name)
            _name_ = int(_name_) if _name_.isdigit() else _name_
            return _name_

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


    def start(self, check=True):
        if not self:
            return

        if check:
            check = Prompt.ask('[red]确认重命名[/red]')
            check = check.lower()
            if check not in ('1', 'true', 'y', 'yes', '\\') or not check:
                print("\n[red]取消重命名[/red]\n")
                return

        print("\n[red]开始重命名[/red]", end="///")
        for file in self.files:
            old = os.path.join(self.folder, file.old_name)
            new = os.path.join(self.folder, file.new_name)
            os.rename(old, new)
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
        table.add_column("new_name", justify="left")
        for file in self.files:
            _old_ = escape(file.old_name)
            _new_ = escape(file.new_name)
            table.add_row(_old_, _new_)
        print(table)
        print()


def change_name(name: str):
    """ 简繁转换 替换不支持的特殊符号 """
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
        name = name.replace(item[0], item[1])
    try:
        name = HanziConv.toSimplified(name)
    except ImportError:
        pass
    finally:
        return name
