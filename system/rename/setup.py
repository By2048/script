import functools
import re
import os
import sys
import typing
import copy
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Union, Any, Callable
from functools import partial
from inspect import isfunction

try:
    from tool.rename import Rename
except ImportError:
    sys.path.append(WindowsPath(__file__).parents[2].as_posix())
    from tool.rename import Rename

try:
    from config import config_rename
except ImportError:
    from .config import config_rename

import fire

rename = Rename()


def rule(file: WindowsPath):
    """ 重命名函数
    @param file: 需要重命名文件的完整路径
    @return: 重命名文件名 命名规则
    """

    # file_name = file.name
    # file_path = file.as_posix()

    for cfg in config_rename:
        if isfunction(cfg) or isinstance(cfg, partial):
            fun = cfg
            try:
                result = fun(file)
            except Exception as e:
                continue
            if result:
                return result
            continue

        _match_, _get_ = cfg[0], cfg[1]

        if not isinstance(_match_, str):
            continue

        if not re.match(_match_, file.name):
            continue

        if isinstance(_get_, str):
            new_name = re.sub(_match_, _get_, file.name)
            file = file.with_name(new_name)
            return file

        if isinstance(_get_, (list, tuple)):
            for _g_ in list(_get_):
                if isinstance(_g_, str):
                    new_name = re.sub(_match_, _g_, file.name)
                    file = file.with_name(new_name)
                elif isfunction(_g_) or isinstance(_g_, partial):
                    file = _g_(file)
            return file


def main(command="", folder="", debug=False):
    if isinstance(folder, str):
        folder = WindowsPath(folder)
    rename.folder = folder or WindowsPath(".")
    rename.rule = rule
    rename.init()
    if debug:
        rename.debug()
    rename.command(command)
    rename.print()
    rename.start()


def debug():
    folder = WindowsPath('T:\\@\\')
    rename.folder = folder
    rename.rule = rule
    rename.init()
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