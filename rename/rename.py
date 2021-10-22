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
    from tool.rename import Rename, version
except ImportError:
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(path)
    from tool.rename import Rename, version

import fire

rename = Rename()


# name : 文件正则处理后的名字
# file : 文件原始完整路径

def _capitalize_(name: str):
    name = name.split("_")
    name[0] = name[0].capitalize()
    return "_".join(name)


def _upper_(name: str):
    name = name.split("_")
    name[0] = name[0].upper()
    return "_".join(name)


def _zfill_(name: str):
    if " " in name:
        index, name = name.split(" ", 1)
        index = index.zfill(2)
        return f"{index} {name}"
    else:
        _name_, _type_ = os.path.splitext(name)
        _name_ = _name_.zfill(2)
        return f"{_name_}{_type_}"


def github(name: str, file: str = ""):
    if "GitHubDesktop" in name:
        _version_ = version(file)
        path_name = Path(name)
        path_file = Path(file)
        path_name = path_name.with_stem(f"{path_name.stem}_{_version_}")
        path_file.with_name(path_name.as_posix())
        return path_name.as_posix()
    return False


def lol(name: str, file: str = ""):
    # 11-18_HN16_NEW-1449121099_05.webm
    if '_HN' in name and '_NEW' in name and name.endswith('.webm'):
        _name_, _type_ = os.path.splitext(name)
        file = os.path.join(rename.folder, name)
        date = os.path.getctime(file)
        date = datetime.fromtimestamp(date).strftime("%Y-%m-%d %H-%M-%S")
        return f"LOL {date}{_type_}"
    return False


def screen(name: str, file: str = ""):
    # Chrome_1618427487075.png
    # 1616779141888 为时间戳
    # 1616779141 -> 2021-03-27 01:19:01
    #        888 -> 毫秒
    if "_" in name and "-" not in name:
        _name_, _type_ = os.path.splitext(name)
        _app_, _date_ = _name_.split("_")
        if len(_date_) != 13 or len(_app_) <= 0:
            return False
        _date_ = _date_[:-3]
        _date_ = int(_date_)
        _date_ = datetime.fromtimestamp(_date_)
        _date_ = _date_.strftime("[%Y-%m-%d][%H-%M-%S]")
        name = f"{_date_}[{_app_}]{_type_}"
        return name
    return False


def screenshot(name: str, file: str = ""):
    # screenshot_1616779141888.png
    # 1616779141888 为时间戳
    # 1616779141 -> 2021-03-27 01:19:01
    #        888 -> 毫秒
    if "screenshot_1" in name or "Screenshot_1" in name:
        name = name.replace("screenshot_", "")
        name = name.replace("Screenshot_", "")
        _name_, _type_ = os.path.splitext(name)
        _name_ = _name_[:-3]
        _name_ = int(_name_)
        _name_ = datetime.fromtimestamp(_name_)
        _name_ = _name_.strftime("%Y-%m-%d %H-%M-%S")
        name = f"{_name_}{_type_}"
        return name
    return False


def timestamp(name: str, file: str = ""):
    # 1616986022655.jpg
    _name_, _type_ = os.path.splitext(name)
    _types_ = ".png .jpg .jpeg .gif .webm"
    if _type_ in _types_.split() and _name_.isdigit() and len(_name_) in [13, 10]:
        if len(_name_) == 13:
            _name_ = _name_[:-3]
        _name_ = int(_name_)
        _name_ = datetime.fromtimestamp(_name_)
        _name_ = _name_.strftime("%Y-%m-%d %H-%M-%S")
        result = f"{_name_}{_type_}"
        return result
    return False


def wx_camera(name: str, file: str = ""):
    # wx_camera_1616986022655.jpg
    if "wx_camera_" not in name:
        return False
    name = name.replace("wx_camera_", "")
    _name_, _type_ = os.path.splitext(name)
    _name_ = _name_[:-3]
    _name_ = int(_name_)
    _name_ = datetime.fromtimestamp(_name_)
    _name_ = _name_.strftime("%Y-%m-%d %H-%M-%S")
    name = f"{_name_}{_type_}"
    return name


def nicotv(name: str, file: str = ""):
    if not re.match(r"第([\d\\.]+)集", name):
        return False
    name = name.replace("(无修)", "")
    data = re.match(r"(第)([\d\\.]+)(集)", name)
    item_name = data.group(2)
    item_name = item_name.zfill(2)
    item_type = name.split('.')[-1]
    return f"{item_name}.{item_type}"


def bilibili(name: str, file: str = ""):
    if not (".mp4" in name and "Av" in name):
        return False

    name = name.split('.')
    try:
        index = name[0].zfill(2)
        name = name[1]
        file_type = name[2]
    except Exception as e:
        print(f'\n文件名解析错误 {name}\n')
        return False

    name = re.split(r'\([avAVpP,\d]+\)', name)  # 去除(Avxxxxxx,Px)
    name = [item for item in name if bool(item)]
    name = ''.join(name)
    name = name.rstrip("_ ")
    new_name = f"{index} {name}.{file_type}"
    return new_name


def bdfilm(name: str, file: str = ""):
    if not ("bd-film.cc" in name or "bd2020" in name):
        return False
    name = name.replace("[BD影视分享bd-film.cc]", "")
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

    github,

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

    # Maye.1.2.6-20211001.zip
    [r"(Maye)(.)(\d.\d.\d)(-)(\d+)(.zip)", r"\1_\3\6"],

    # VeraCrypt_1.24-Update7.zip
    [r"(VeraCrypt)(_)([\d+\.]+)(-Update)(\d)(.zip)", r"\1\2\3.\5\6"],
    # VeraCrypt Setup 1.24-Update7
    [r"(VeraCrypt)( Setup )([\d+\.]+)(-Update)(\d)(.exe)", r"\1_\3.\5\6"],

    # go1.16.3.windows-amd64.zip
    [r"(go)([\d+\.]+)(.windows-amd64)(.zip)", (r"\1_\2\4", _capitalize_)],

    # VMware-workstation-full-16.1.0-17198959.exe
    [r"(VMware)(-workstation-full-)([\d+\.]+)(-)(\d+)(.exe)", r"\1_\3.\5\6"],

    # Sandboxie-Plus-x64-v0.9.6.exe
    [r"(Sandboxie)(-Plus)(-x64)(-v)([\d+\.]+)(.exe)", r"\1_\5\6"],

    # XMind-for-Windows-64bit-11.1.1-202110191919.exe
    [r"(XMind)(-for)(-Windows)(-64bit)(-)([\d+\.]+)(-\d+)(.exe)", r"\1_\6\8"],

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

    #  [Keep] XMind.lnk
    [r"(\[)(Keep)(\])(\s)([\d\w]+)(.lnk)", r"\1#\3\5\6"],

    # 〔98'〕
    [r"(〔)([\s\S]+)(〕)(\.\w+)", (r"\2\4", lambda x: x.replace("'", " "))],

    # 950618(950618)_20210627205223.mp3
    [r"([\s\S]+)(\()(\d+)(\))(_)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.mp3)",
     r"(\6-\7-\8)(\9\-\10-\11)(\3)(\1)\12"],

]

config = config_software + config_image_video + config_other


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
