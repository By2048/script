import re
import os
import sys
import typing
import copy
from typing import Union, Any, Callable
from functools import partial
from inspect import isfunction

try:
    from tool.rename import Rename
except ImportError:
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(path)
    from tool.rename import Rename

import fire


def _capitalize_(item: str):
    item = item.split("_")
    item[0] = item[0].capitalize()
    return "_".join(item)


def _upper_(item: str):
    item = item.split("_")
    item[0] = item[0].upper()
    return "_".join(item)


def _zfill_(item: str):
    _name_, _type_ = item.split(".")
    _name_ = _name_.zfill(2)
    return f"{_name_}.{_type_}"


# 替换规则
config = [

    # Xftp-7.0.0063p.exe
    [r"(Xftp)(-)([\d\.]+)(\w)(.exe)", r"\1_\3\5"],

    # Xshell-7.0.0063p.exe
    [r"(Xshell)(-)([\d\.]+)(\w)(.exe)", r"\1_\3\5"],

    # ventoy-1.0.38-windows.zip
    [r"(ventoy)(-)([\d\.]+)(-windows)(.zip)", (r"\1_\3\5", _capitalize_)],

    # rdm-2021.3.0.0.exe
    [r"(rdm)(-)([\d\.]+)(.exe)", (r"\1_\3\4", _upper_)],

    # Screenshot_20210318215042.png
    [r"(Screenshot_)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.png)", r"\2-\3-\4 \5-\6-\7\8"],

    # FreeFileSync_11.8_Windows_Setup.exe
    [r"(FreeFileSync_)([\d+\.]+)(_Windows_Setup)(.exe)", r"\1\2\4"],

    # python-3.8.5.exe
    [r"(python)(-)([\d\.]+)(.exe)", (r"\1_\3\4", _capitalize_)],
    # python-3.9.2-amd64.exe
    [r"(python)(-)([\d\.]+)(-amd64)(.exe)", (r"\1_\3\5", _capitalize_)],

    # DG5411178_x64.zip
    [r"(DG)(\d+)(_x64)(.zip)", r"DiskGenius_\2\4"],

    # Everything-1.4.1.1005.x64.zip
    [r"(Everything)(-)([\d\.]+)(.x64)(.zip)", r"\1_\3\5"],
    # Everything-1.4.1.1005.x64-Setup.exe
    [r"(Everything)(-)([\d\.]+)(.x64-Setup)(.exe)", r"\1_\3\5"],

    # ScreenToGif.2.27.3.Setup.msi
    [r"(ScreenToGif)(\.)([\d\.]+)(.Setup)(.msi)", r"\1_\3\5"],
    # ScreenToGif.2.27.3.Portable.zip
    [r"(ScreenToGif)(\.)([\d\.]+)(.Portable)(.zip)", r"\1_\3\5"],

    # Git-2.31.0-64-bit.exe
    [r"(Git)(-)([\d\.]+)(-64-bit)(.exe)", r"\1_\3\5"],
    # PortableGit-2.31.0-64-bit.7z.exe
    [r"(Portable)(Git)(-)([\d\.]+)(-64-bit)(.7z)(.exe)", r"\2_\4\6\7"],

    # Q-Dir_Portable_x64.zip
    [r"(Q-Dir)(_)(Portable_x64)(.zip)", r"\1\4"],
    # Q-Dir_x64.exe
    [r"(Q-Dir)(_)(x64)(.exe)", r"\1\4"],

    # go1.16.3.windows-amd64.zip
    [r"(go)([\d+\.]+)(.windows-amd64)(.zip)", (r"\1_\2\4", _capitalize_)],

    # VMware-workstation-full-16.1.0-17198959.exe
    [r"(VMware)(-workstation-full-)([\d+\.]+)(-)(\d+)(.exe)", r"\1_\3.\5\6"],

    # FoxmailSetup_7.2.20.273.exe
    [r"(Foxmail)(Setup)(_)([\d\.]+)(.exe)", r"\1\3\4\5"],

    # IMG_20200926_214521.jpg
    [r"(IMG_)(\d{4})(\d{2})(\d{2})(_)(\d{2})(\d{2})(\d{2})(.jpg)", r"\2-\3-\4 \6-\7-\8\9"],

    # PowerToysSetup-0.36.0-x64.exe
    [r"(PowerToys)(Setup-)([\d\.]+)(-x64)(.exe)", r"\1_\3\5"],

    # 第xxx集
    [r"(第)(\d+)(集)(\.\w+)", (r"\2\4", _zfill_)],

    # 〔98'〕
    [r"(〔)([\s\S]+)(〕)(\.\w+)", (r"\2\4", lambda x: x.replace("'", " "))],

    # Test
    [lambda x: "v2" in x, lambda x: x.replace("v2-", "")]

]


def rule(item: str):
    for cfg in config:
        _match_ = cfg[0]
        _all_get_ = cfg[1]

        check = False
        if isinstance(_match_, str):
            if re.match(_match_, item):
                check = True
        elif isfunction(_match_):
            if _match_(item):
                check = True

        if not check:
            continue

        if isfunction(_all_get_):
            item = _all_get_(item)
            return item
        elif isinstance(_all_get_, str):
            item = re.sub(_match_, _all_get_, item)
        elif isinstance(_all_get_, (list, tuple)):
            for _get_ in list(_all_get_):
                if isinstance(_get_, str):
                    item = re.sub(_match_, _get_, item)
                elif isfunction(_get_):
                    item = _get_(item)

        return item


def main(folder="", debug=False):
    rename = Rename()
    rename.folder = folder or os.getcwd()
    rename.rule = rule
    rename.init()
    if debug:
        rename.debug()
    rename.command()
    rename.print()
    rename.start()


if __name__ == '__main__':
    fire.Fire(main)
