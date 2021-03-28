import inspect
import os
import sys
from typing import List

from rich import print
from rich import box
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.table import Table
from hanziconv import HanziConv


class File(object):
    def __init__(self, old_name='', new_name=''):
        self.old_name = old_name
        self.new_name = new_name

    def __str__(self):
        return f"{self.old_name} \t {self.new_name}"


class Rename(object):
    def __init__(self):
        self._folder_: str = ""  # 重命名文件夹目录
        self.files: List[File] = []  # 需要重命名的文件 新名字-旧名字
        self.function_need_rename = None  # 筛选需要重命名的文件
        self.function_get_name = None  # 重命名函数

    @property
    def folder(self):
        return self._folder_

    @folder.setter
    def folder(self, value):
        if sys.argv[-1] == ".":
            self._folder_ = os.getcwd()
        else:
            self._folder_ = value

    def __bool__(self):
        return bool(len(self.files))

    def init(self):
        for item in os.listdir(self.folder):
            if not self.function_need_rename(item):
                continue
            file = File(old_name=item)
            file.new_name = self.function_get_name(item)
            file.new_name = change_name(file.new_name)
            self.files.append(file)
        self.sort()

    def sort(self):

        def key(item: File):
            _name_, _type_ = os.path.splitext(item.new_name)
            return int(_name_) if _name_.isdigit() else _name_

        self.files = sorted(self.files, key=key)

    def command(self):
        arg = sys.argv[-1]
        if len(sys.argv) == 1:
            return

        if arg == "test":
            self.print()
            exit()

        if arg == "rule":
            need_rename = inspect.getsource(self.function_need_rename)
            get_name = inspect.getsource(self.function_get_name)
            print()
            print(Syntax(need_rename, "python3", line_numbers=True, indent_guides=True))
            print()
            print(Syntax(get_name, "python3", line_numbers=True, indent_guides=True))
            print()
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
            table.add_row(file.old_name, file.new_name)
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
