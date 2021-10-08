import re
import os
import sys
import typing
import copy
from datetime import datetime
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

rename = Rename()


def _capitalize_(item: str):
    item = item.split("_")
    item[0] = item[0].capitalize()
    return "_".join(item)


def _upper_(item: str):
    item = item.split("_")
    item[0] = item[0].upper()
    return "_".join(item)


def _zfill_(item: str):
    if " " in item:
        index, name = item.split(" ", 1)
        index = index.zfill(2)
        return f"{index} {name}"
    else:
        _name_, _type_ = os.path.splitext(item)
        _name_ = _name_.zfill(2)
        return f"{_name_}{_type_}"


def lol(item: str):
    # 11-18_HN16_NEW-1449121099_05.webm
    if '_HN' in item and '_NEW' in item and item.endswith('.webm'):
        _name_, _type_ = os.path.splitext(item)
        file = os.path.join(rename.folder, item)
        date = os.path.getctime(file)
        date = datetime.fromtimestamp(date).strftime("%Y-%m-%d %H-%M-%S")
        return f"LOL {date}{_type_}"
    return False


def screen(item):
    # Chrome_1618427487075.png
    # 1616779141888 为时间戳
    # 1616779141 -> 2021-03-27 01:19:01
    #        888 -> 毫秒
    if "_" in item and "-" not in item:
        _name_, _type_ = os.path.splitext(item)
        _app_, _date_ = _name_.split("_")
        if len(_date_) != 13 or len(_app_) <= 0:
            return False
        _date_ = _date_[:-3]
        _date_ = int(_date_)
        _date_ = datetime.fromtimestamp(_date_)
        _date_ = _date_.strftime("[%Y-%m-%d][%H-%M-%S]")
        item = f"{_date_}[{_app_}]{_type_}"
        return item
    else:
        return False


def screenshot(item):
    # screenshot_1616779141888.png
    # 1616779141888 为时间戳
    # 1616779141 -> 2021-03-27 01:19:01
    #        888 -> 毫秒
    if "screenshot_1" in item or "Screenshot_1" in item:
        item = item.replace("screenshot_", "")
        item = item.replace("Screenshot_", "")
        _name_, _type_ = os.path.splitext(item)
        _name_ = _name_[:-3]
        _name_ = int(_name_)
        _name_ = datetime.fromtimestamp(_name_)
        _name_ = _name_.strftime("%Y-%m-%d %H-%M-%S")
        item = f"{_name_}{_type_}"
        return item
    else:
        return False


def timestamp(item: str):
    # 1616986022655.jpg
    _name_, _type_ = os.path.splitext(item)
    _types_ = ".png .jpg .jpeg .gif .webm"
    if _type_ in _types_.split() and _name_.isdigit() and len(_name_) in [13, 10]:
        if len(_name_) == 13:
            _name_ = _name_[:-3]
        _name_ = int(_name_)
        _name_ = datetime.fromtimestamp(_name_)
        _name_ = _name_.strftime("%Y-%m-%d %H-%M-%S")
        result = f"{_name_}{_type_}"
        return result
    else:
        return False


def wx_camera(item: str):
    # wx_camera_1616986022655.jpg
    if "wx_camera_" not in item:
        return False
    item = item.replace("wx_camera_", "")
    _name_, _type_ = os.path.splitext(item)
    _name_ = _name_[:-3]
    _name_ = int(_name_)
    _name_ = datetime.fromtimestamp(_name_)
    _name_ = _name_.strftime("%Y-%m-%d %H-%M-%S")
    item = f"{_name_}{_type_}"
    return item


def nicotv(item: str):
    if not re.match(r"第([\d\\.]+)集", item):
        return False
    item = item.replace("(无修)", "")
    data = re.match(r"(第)([\d\\.]+)(集)", item)
    item_name = data.group(2)
    item_name = item_name.zfill(2)
    item_type = item.split('.')[-1]
    return f"{item_name}.{item_type}"


def bilibili(item: str):
    if not (".mp4" in item and "Av" in item):
        return False

    item = item.split('.')
    try:
        index = item[0].zfill(2)
        name = item[1]
        file_type = item[2]
    except Exception as e:
        print(f'\n文件名解析错误 {item}\n')
        return False

    name = re.split(r'\([avAVpP,\d]+\)', name)  # 去除(Avxxxxxx,Px)
    name = [item for item in name if bool(item)]
    name = ''.join(name)
    name = name.rstrip("_ ")
    new_name = f"{index} {name}.{file_type}"
    return new_name


def bdfilm(item: str):
    if not ("bd-film.cc" in item or "bd2020" in item):
        return False
    name = item.replace("[BD影视分享bd-film.cc]", "")
    name = name.replace("[BD影视分享bd2020.com]", "")
    name = name.strip()
    name = name.replace(':', ' ')
    name = name.replace('：', ' ')
    _name_, *_, _type_ = name.split('.')
    _type_ = _type_.replace("mp41", "mp4")
    return f"{_name_}.{_type_}"


config_image_video = [

    # 手机屏幕截图
    screen,
    screenshot,

    # 以时间戳格式保存的图片
    timestamp,

    # 微信保存的图片
    wx_camera,

    lol,

    # 20210622183532.jpg
    [r"(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.jpg)", r"\1-\2-\3 \4-\5-\6\7"],

    # Screenshot_20210318215042.png
    [r"(Screenshot_)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.png)", r"\2-\3-\4 \5-\6-\7\8"],

    # Screenshot_2014-08-31-13-59-51.png
    [r"(Screenshot_)(\d{4}\-\d{2}\-\d{2})(\-)(\d{2}\-\d{2}\-\d{2})(.png)", r"\2 \4\5"],

    # Screenshot_2013-11-29-13-01-53-1.png
    [r"(Screenshot_)(\d{4}\-\d{2}\-\d{2})(\-)(\d{2}\-\d{2}\-\d{2})(\-1)(.png)", r"\2 \4\6"],

    # IMG20200712095720.jpg
    [r"(IMG)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.jpg)", r"\2-\3-\4 \5-\6-\7\8"],

    # IMG_20200926_214521.jpg
    [r"(IMG_)(\d{4})(\d{2})(\d{2})(_)(\d{2})(\d{2})(\d{2})(.jpg)", r"\2-\3-\4 \6-\7-\8\9"],

    # IMG_20040622_141354_HDR.jpg
    [r"(IMG_)(\d{4})(\d{2})(\d{2})(_)(\d{2})(\d{2})(\d{2})(_HDR)(.jpg)", r"\2-\3-\4 \6-\7-\8\10"],

    # PANO_20140629_080915.jpg
    [r"(PANO_)(\d{4})(\d{2})(\d{2})(_)(\d{2})(\d{2})(\d{2})(.jpg)", r"\2-\3-\4 \6-\7-\8\9"],

    # VID_20210731_144747.mp4
    [r"(VID_)(\d{4})(\d{2})(\d{2})(_)(\d{2})(\d{2})(\d{2})(.mp4|.3gp)", r"\2-\3-\4 \6-\7-\8\9"],

    # Recorder_20210903135016.mp4
    [r"(Recorder_)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.mp4)", r"\2-\3-\4 \5-\6-\7\8"],

]

config_software = [

    # Xftp-7.0.0063p.exe
    [r"(Xftp)(-)([\d\.]+)(\w)(.exe)", r"\1_\3\5"],

    # Xshell-7.0.0063p.exe
    [r"(Xshell)(-)([\d\.]+)(\w)(.exe)", r"\1_\3\5"],

    # ventoy-1.0.38-windows.zip
    [r"(ventoy)(-)([\d\.]+)(-windows)(.zip)", (r"\1_\3\5", _capitalize_)],

    # navicat150_premium_cs_x64.exe
    [r"(navicat)([\d]+)(_premium_cs_x64)(.exe)", (r"\1_\2\4", _capitalize_)],

    # rdm-2021.3.0.0.exe
    [r"(rdm)(-)([\d\.]+)(.exe)", (r"\1_\3\4", _upper_)],

    # FreeFileSync_11.8_Windows_Setup.exe
    [r"(FreeFileSync_)([\d+\.]+)(_Windows_Setup)(.exe)", r"\1\2\4"],

    # python-3.8.5.exe
    [r"(python)(-)([\d\.]+)(.exe)", (r"\1_\3\4", _capitalize_)],
    # python-3.9.2-amd64.exe
    [r"(python)(-)([\d\.]+)(-amd64)(.exe)", (r"\1_\3\5", _capitalize_)],
    # python-3.9.5-embed-amd64.zip
    [r"(python)(-)([\d\.]+)(-embed-amd64)(.zip)", (r"\1_\3\5", _capitalize_)],

    # node-v14.17.0-win-x64.zip
    [r"(node)(-v)([\d\.]+)(-win-x64)(.zip)", (r"\1_\3\5", _capitalize_)],

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

]

# 替换规则
# 函数 \ 正则表达式
config_other = [

    # 下载的动漫
    # nicotv,

    bilibili,

    bdfilm,

    # pattern.cpython-37.pyc
    [r"(\w+)(\.cpython-37)(\.pyc)", r"\1\3"],

    # MuMu20210129215157.png
    [r"(MuMu)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.png)", r"\2-\3-\4 \5-\6-\7\8"],

    # PowerToysSetup-0.36.0-x64.exe
    [r"(PowerToys)(Setup-)([\d\.]+)(-x64)(.exe)", r"\1_\3\5"],

    # xxx(无修).mp4
    [r"(.*)(\(无修\))([\.\w\d]+)", (r"\1\3")],

    # 第1集
    # 第xxx集
    [r"(第)(\d+)(集|话)(\s)(\S+)", (r"\2 \5", _zfill_)],
    [r"(第)(\d+)(集|话)([\.\w\d]+)", (r"\2\4", _zfill_)],

    # 〔98'〕
    [r"(〔)([\s\S]+)(〕)(\.\w+)", (r"\2\4", lambda x: x.replace("'", " "))],

    # 950618(950618)_20210627205223.mp3
    [r"([\s\S]+)(\()(\d+)(\))(_)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.mp3)",
     r"(\6-\7-\8)(\9\-\10-\11)(\3)(\1)\12"],

]

config = config_software + config_image_video + config_other


def rule(item: str):
    for cfg in config:

        if isfunction(cfg):
            try:
                result = cfg(item)
            except Exception as e:
                continue
            if result:
                return result, cfg
            continue

        _match_, _get_ = cfg[0], cfg[1]

        if not isinstance(_match_, str):
            continue

        if not re.match(_match_, item):
            continue

        if isinstance(_get_, str):
            result = re.sub(_match_, _get_, item)
            return result, cfg

        if isinstance(_get_, (list, tuple)):
            result = None
            for _g_ in list(_get_):
                if isinstance(_g_, str):
                    result = re.sub(_match_, _g_, item)
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
