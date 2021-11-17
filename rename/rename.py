import re
import os
import sys
import typing
import copy
from datetime import datetime
from pathlib import Path
from typing import Union, Any, Callable
from functools import partial
from inspect import isfunction

try:
    from config import config
    from tool.rename import Rename
except ImportError:
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(path)
    from tool.rename import Rename

import fire

rename = Rename()


def rule(file: Path):
    """ 重命名函数
    @param file: 需要重命名文件的完整路径
    @return: 重命名文件名 命名规则
    """

    file_name = file.name
    file_path = file.as_posix()

    for cfg in config:

        if isfunction(cfg):
            fun = cfg
            try:
                result = fun(file_name, file_path)
            except Exception as e:
                continue
            if result:
                return result, cfg
            continue

        _match_, _get_ = cfg[0], cfg[1]

        if not isinstance(_match_, str):
            continue

        if not re.match(_match_, file_name):
            continue

        if isinstance(_get_, str):
            result = re.sub(_match_, _get_, file_name)
            return result, cfg

        if isinstance(_get_, (list, tuple)):
            result = None
            for _g_ in list(_get_):
                if isinstance(_g_, str):
                    result = re.sub(_match_, _g_, file_name)
                elif isfunction(_g_):
                    result = _g_(result)
            return result, cfg


def main(command="", folder="", debug=False):
    rename.folder = folder or os.getcwd()
    rename.rule = rule
    rename.init()
    if debug:
        rename.debug()
    rename.command(command)
    rename.print()
    rename.start()


def debug():
    folder = 'T:\\'
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
