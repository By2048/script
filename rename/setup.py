import functools
import re
import os
import sys
import typing
import copy
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Union, Any, Callable

from rename import Rename
from config import config

import fire

rename = Rename()


def main(command="", folder=".", debug=False):
    if isinstance(folder, str):
        folder = WindowsPath(folder)
    rename.folder = folder or WindowsPath(".")
    rename.config = config
    rename.init()
    rename.command(command)
    if debug:
        rename.debug()
    rename.print()
    rename.start()
    if rename.duplicate:
        rename.remove_duplicate()


def debug():
    folder = WindowsPath('T:\\')
    rename.config = config
    rename.folder = folder
    rename.init()
    rename.command("debug")
    rename.print()


def test():
    # 1616779141888 为时间戳
    # 1616779141 -> 2021-03-27 01:19:01
    #        888 -> 毫秒
    # date = "1616779141888"
    # print(_timestamp_(date))
    pass


if __name__ == '__main__':
    # test()
    # debug()
    fire.Fire(main)