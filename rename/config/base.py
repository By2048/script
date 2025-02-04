import re
import os
import sys
import typing
import copy
import hashlib
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Union, Any, Callable
from functools import partial
from inspect import isfunction

try:
    sys.path.insert(0, WindowsPath(__file__).parents[2].as_posix())
    from tool.file import get_exe_file_version, get_exe_product_version, lnk_to_exe
except ImportError:
    print("import error")


# name : 文件正则处理后的名字
# file : 文件原始完整路径

def upper_x(file: WindowsPath, index=-1):
    stem = file.stem
    if index == -1:
        stem = stem.upper()
    elif index == 0:
        stem = stem
    elif index > 0:
        stem = stem[0:index].upper() + stem[index:]
    file = file.with_stem(stem)
    return file


upper_1 = partial(upper_x, index=1)
upper_2 = partial(upper_x, index=2)
upper_3 = partial(upper_x, index=3)
upper_4 = partial(upper_x, index=4)
upper_5 = partial(upper_x, index=5)
upper_all = partial(upper_x, index=-1)


def version_x(file: WindowsPath, match: str, get: str):
    if not file.as_posix().endswith(".exe"):
        return
    if match.lower() not in file.name.lower():
        return
    version_data = get_exe_file_version(file)
    if version_data:
        new_name = f"{get}_{version_data}.exe"
    else:
        new_name = f"{get}.exe"
    file = file.with_name(new_name)
    return file


# 以时间戳格式保存的文件
def timestamp(file: WindowsPath):
    stem = file.stem
    if not stem.isdigit():
        return
    if len(stem) not in [13, 10]:
        return
    if len(stem) == 13:
        stem = stem[:-3]
    stem = int(stem)
    stem = datetime.fromtimestamp(stem)
    stem = stem.strftime("%Y-%m-%d_%H-%M-%S")
    file = file.with_stem(stem)
    return file


def timestamp_with_x(file: WindowsPath, xxx: str):
    stem = file.stem.lower()
    if xxx not in stem:
        return
    stem = stem.replace(xxx, "")
    if not stem.isdigit():
        return
    if len(stem) not in [13, 10]:
        return
    if len(stem) == 13:  # 去除毫秒数据
        stem = stem[:-3]
    stem = int(stem)
    try:
        stem = datetime.fromtimestamp(stem)
        stem = stem.strftime("%Y-%m-%d_%H-%M-%S")
    except:  # noqa
        return
    file = file.with_stem(stem)
    return file


def capitalize(file: WindowsPath):
    stem = file.stem
    stem = stem.capitalize()
    file = file.with_stem(stem)
    return file


def zfill(file: WindowsPath):
    if " " in file.stem:
        index, name = file.stem.split(" ", 1)
        index = index.zfill(2)
        new_stem = f"{index} {name}"
        file = file.with_stem(new_stem)
        return file
    else:
        new_stem = file.stem.zfill(2)
        file = file.with_stem(new_stem)
        return file


def md5(file: WindowsPath):
    hash_md5 = hashlib.md5()
    with open(file, "rb") as content:
        while chunk := content.read(4096):
            hash_md5.update(chunk)
    hash_md5 = hash_md5.hexdigest()
    file = file.with_stem(hash_md5)
    return file