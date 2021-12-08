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
    from tool.rename import Rename, get_version
except ImportError:
    sys.path.append(WindowsPath(__file__).parents[1].as_posix())
    from tool.rename import Rename, get_version


# name : 文件正则处理后的名字
# file : 文件原始完整路径

def _capitalize_(file: WindowsPath):
    new_name = file.name.split("_")
    new_name[0] = new_name[0].capitalize()
    new_name = "_".join(new_name)
    file = file.with_name(new_name)
    return file


def _upper_(file: WindowsPath):
    new_name = file.name.split("_")
    new_name[0] = new_name[0].upper()
    new_name = "_".join(new_name)
    file = file.with_name(new_name)
    return file


def _zfill_(file: WindowsPath):
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


def github(file: WindowsPath):
    key = 'GitHubDesktop'
    new_name = ""
    if key in file.name:
        version = get_version(file)
        # path_name = Path(name)
        # path_file = Path(file)
        # path_name = path_name.with_stem(f"{path_name.stem}_{_version_}")
        # path_file.with_name(path_name.as_posix())
        # return path_name.as_posix()
        new_name = f"{key}_{version}.exe"
    if file.name == new_name:
        return file
    file = file.with_name(new_name)
    return file


def potplayer(file: WindowsPath):
    key = 'PotPlayer'
    new_name = ""
    if key in file.name:
        version = get_version(file)
        new_name = f"{key}_{version}.exe"
    if file.name == new_name:
        return file
    file = file.with_name(new_name)
    return file


def fdm(file: WindowsPath):
    key = 'fdm'
    new_name = ""
    if key in file.name:
        version = get_version(file)
        new_name = f"{key.upper()}_{version}.exe"
    if file.name == new_name:
        return file
    file = file.with_name(new_name)
    return file


def lol(file: WindowsPath):
    # 11-18_HN16_NEW-1449121099_05.webm
    if '_HN' in file.name and '_NEW' in file.name and file.name.endswith('.webm'):
        date = file.stat().st_ctime
        date = datetime.fromtimestamp(date).strftime("%Y-%m-%d %H-%M-%S")
        file = file.with_stem(f"LOL {date}")
        return file
    return file


def screen(file: WindowsPath):
    # Chrome_1618427487075.png
    # 1616779141888 为时间戳
    # 1616779141 -> 2021-03-27 01:19:01
    #        888 -> 毫秒
    if "_" in file.name and "-" not in file.name:
        _app_, _date_ = file.stem.split("_")
        if len(_date_) != 13 or len(_app_) <= 0:
            return file
        _date_ = _date_[:-3]
        _date_ = int(_date_)
        _date_ = datetime.fromtimestamp(_date_)
        _date_ = _date_.strftime("[%Y-%m-%d][%H-%M-%S]")
        file = file.with_stem(f"{_date_}[{_app_}]")
        return file
    return file


def screenshot(file: WindowsPath):
    # screenshot_1616779141888.png
    # 1616779141888 为时间戳
    # 1616779141 -> 2021-03-27 01:19:01
    #        888 -> 毫秒
    if "screenshot_1" in file.name or "Screenshot_1" in file.name:
        file.stem = file.stem.replace("screenshot_", "")
        file.stem = file.stem.replace("Screenshot_", "")
        new_stem = int(file.stem)
        new_stem = datetime.fromtimestamp(new_stem)
        new_stem = new_stem.strftime("%Y-%m-%d %H-%M-%S")
        file = file.with_stem(new_stem)
        return file
    return file


def timestamp(file: WindowsPath):
    # 1616986022655.jpg
    _type_ = file.suffix
    _types_ = ".png .jpg .jpeg .gif .webm"
    if _type_ in _types_.split() and file.stem.isdigit() and len(file.stem) in [13, 10]:
        if len(file.stem) == 13:
            file.stem = file.stem[:-3]
        new_stem = int(file.stem)
        new_stem = datetime.fromtimestamp(new_stem)
        new_stem = new_stem.strftime("%Y-%m-%d %H-%M-%S")
        file = file.with_stem(new_stem)
        return file
    return file


def wx_camera(file: WindowsPath):
    # wx_camera_1616986022655.jpg
    if "wx_camera_" not in file.name:
        return False
    file.stem = file.stem.replace("wx_camera_", "")

    new_stem = file.stem[:-3]
    new_stem = int(new_stem)
    new_stem = datetime.fromtimestamp(new_stem)
    new_stem = new_stem.strftime("%Y-%m-%d %H-%M-%S")
    file = file.with_stem(new_stem)
    return file


def nicotv(file: WindowsPath):
    if not re.match(r"第([\d\\.]+)集", file.stem):
        return file
    file.stem = file.stem.replace("(无修)", "")
    data = re.match(r"(第)([\d\\.]+)(集)", file.stem)
    item_stem = data.group(2)
    item_stem = item_stem.zfill(2)
    file = file.with_stem(item_stem)
    return file


def bilibili(file: WindowsPath):
    if ".mp4" not in file.name or "Av" not in file.name:
        return file

    info = file.name.split('.')
    try:
        index = info[0].zfill(2)
        name = info[1]
        file_type = info[2]
    except Exception as e:
        print(f'\n文件名解析错误 {file.name}\n')
        return False

    name = re.split(r'\([avAVpP,\d]+\)', name)  # 去除(Avxxxxxx,Px)
    name = [item for item in name if bool(item)]
    name = ''.join(name)
    name = name.rstrip("_ ")
    new_stem = f"{index} {name}"
    file = file.with_stem(new_stem)
    return file


def bdfilm(file: WindowsPath):
    if "bd-film.cc" not in file.name or "bd2020" not in file.name:
        return file

    name = file.name
    name = name.replace("[BD影视分享bd-film.cc]", "")
    name = name.replace("[BD影视分享bd2020.com]", "")
    name = name.replace("mp41", "mp4")
    name = name.strip()
    name = name.replace(':', ' ')
    name = name.replace('：', ' ')

    file = file.with_name(name)
    return file


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

    potplayer,

    fdm,

    # Xftp-7.0.0063p.exe
    [r"(Xftp)(-)([\d\.]+)(\w)(.exe)", r"\1_\3\5"],

    # Xshell-7.0.0063p.exe
    [r"(Xshell)(-)([\d\.]+)(\w)(.exe)", r"\1_\3\5"],

    # aria2-1.36.0-win-64bit-build1.zip
    [r"(aria2)(-)([\d\.]+)(-win-64bit-build1)(.zip)", (r"\1_\3\5", _capitalize_)],

    # dexpot_1614_portable_r2439.zip
    [r"(dexpot)(_)([\d\.]+)(_portable)(\_\w+)(.zip)", (r"\1_\3\6", _capitalize_)],
    # dexpot_1614_r2439.exe
    [r"(dexpot)(_)([\d\.]+)(\_\w+)(.exe)", (r"\1_\3\5", _capitalize_)],

    # ventoy-1.0.38-windows.zip
    [r"(ventoy)(-)([\d\.]+)(-windows)(.zip)", (r"\1_\3\5", _capitalize_)],

    # ffmpeg-2021-11-18-git-85a6b7f7b7-full_build.7z
    [r"(ffmpeg)(-)([\d\-]+)(-git)(\-\w+)(-full_build)(.7z)", r"\1_\3\7"],

    # navicat150_premium_cs_x64.exe
    [r"(navicat)([\d]+)(_premium_cs_x64)(.exe)", (r"\1_\2\4", _capitalize_)],

    # cloudmusicsetup2.9.5.199424.exe
    [r"(cloudmusic)(setup)([\d\.]+)(.exe)", r"CloudMusic_\3\4"],

    # rdm-2021.3.0.0.exe
    [r"(rdm)(-)([\d\.]+)(.exe)", (r"\1_\3\4", _upper_)],

    # QuiteRSS-0.19.4.zip
    [r"(QuiteRSS)(-)([\d\.]+)(.zip)", r"\1_\3\4"],

    # FreeFileSync_11.8_Windows_Setup.exe
    [r"(FreeFileSync_)([\d\.]+)(_Windows_Setup)(.exe)", r"\1\2\4"],

    # SumatraPDF-3.3.3-64.zip  portable (zip) v
    [r"(SumatraPDF)(\-)([\d\.]+)(-64)(\.zip)", r"\1_\3_Portable\5"],
    # SumatraPDF-3.3.3-64-install.exe
    [r"(SumatraPDF)(\-)([\d\.]+)(-64)(-install)(\.exe)", r"\1_\3_Install\6"],

    # sysdiag-all-5.0.64.2-2021.11.3.1.exe
    [r"(sysdiag)(\-all\-)([\d\.]+)(\-)([\d\.]+)(.exe)", r"HuoRong_\3\6"],

    # WiresharkPortable_3.4.9.paf.exe
    [r"(Wireshark)(Portable)(_)([\d\.]+)(.paf)(.exe)", r"\1_\4\6"],

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
    # Q-Dir_Portable_x64_9.97.zip
    [r"(Q-Dir)(_)(Portable_x64)(_)([\d\.]+)(.zip)", r"\1\2\5\6"],
    # Q-Dir_x64.exe
    [r"(Q-Dir)(_)(x64)(.exe)", r"\1\4"],

    # calibre-portable-installer-5.32.0.exe
    [r"(calibre)(-portable-installer-)([\d\.]+)(.exe)", (r"\1_\3\4", _capitalize_)],

    # VSCodeSetup-x64-1.61.2.exe
    [r"(VSCode)(Setup)(-x64-)([\d\.]+)(.exe)", r"\1_\4\5"],

    # AutoHotkey_1.1.33.10_setup.exe
    [r"(AutoHotkey)(_)([\d\.]+)(_setup)(.exe)", r"\1_\3\5"],

    # Maye.1.2.6-20211001.zip
    [r"(Maye)(.)(\d.\d.\d)(-)(\d+)(.zip)", r"\1_\3\6"],

    # VeraCrypt_1.24-Update7.zip
    [r"(VeraCrypt)(_)([\d\.]+)(-Update)(\d)(.zip)", r"\1\2\3.\5\6"],
    # VeraCrypt Setup 1.24-Update7
    [r"(VeraCrypt)( Setup )([\d\.]+)(-Update)(\d)(.exe)", r"\1_\3.\5\6"],

    # go1.17.3.windows-arm64.zip
    [r"(go)([\d\.]+)(.windows-)(amd64)(.zip)", (r"\1_\2\5", _capitalize_)],

    # jdk-17_windows-x64_bin.zip
    [r"(jdk)(-)([\d\.]+)(_windows)(-x64_bin)(.zip)", r"\1_\3\6"],

    # frp_0.38.0_windows_amd64.zip
    [r"(frp)(_)([\d\.]+)(_windows_amd64)(.zip)", (r"\1_\3\5", _capitalize_)],

    # Shadowsocks-4.4.0.185.zip
    [r"(Shadowsocks)(-)([\d\.]+)(.zip)", r"\1_\3\4"],

    # VMware-workstation-full-16.1.0-17198959.exe
    [r"(VMware)(-workstation-full-)([\d\.]+)(-)(\d+)(.exe)", r"\1_\3.\5\6"],

    # VirtualBox-6.1.28-147628-Win.exe
    [r"(VirtualBox)(-)([\d\.]+)(-)(\d+)(-Win)(.exe)", r"\1_\3.\5\7"],
    # Oracle_VM_VirtualBox_Extension_Pack-6.1.28.vbox-extpack
    [r"(Oracle_VM_)(VirtualBox)(_Extension_Pack)(-)([\d\.]+)(.vbox-extpack)", r"\2_\5\6"],

    # Sandboxie-Plus-x64-v0.9.6.exe
    [r"(Sandboxie)(-Plus)(-x64)(-v)([\d\.]+)(.exe)", r"\1_\5\6"],

    # XMind-for-Windows-64bit-11.1.1-202110191919.exe
    [r"(XMind)(-for)(-Windows)(-64bit)(-)([\d\.]+)(-\d+)(.exe)", r"\1_\6\8"],

    # FoxmailSetup_7.2.20.273.exe
    [r"(Foxmail)(Setup)(_)([\d\.]+)(.exe)", r"\1\3\4\5"],

    # npp.8.1.9.portable.x64.zip
    [r"(npp.)([\d\.]+)(.portable)(.x64)(.zip)", r"Notepad++_\2\5"],

    # QuickLook-3.7.0.zip
    [r"(QuickLook)(-)([\d\.]+)(.zip)", r"\1_\3\4"],

    # Firefox Setup 94.0.1.exe
    [r"(Firefox)(\s)(Setup)(\s)([\d\.]+)(.exe)", r"\1_\5\6"],

    # Snipaste-2.6.6-Beta-x64.zip
    [r"(Snipaste)(-)([\d\.]+)(-Beta-x64)(.zip)", r"\1_\3\5"],

    # jetbrains-toolbox-1.22.10685.exe
    [r"(jetbrains)(-)(toolbox)(-)([\d\.]+)(.exe)", (r"\1_\5\6", _capitalize_)],

    # Samsung_Magician_Installer_Official_7.0.0.510.zip
    [r"(Samsung_)(Magician)(_Installer)(_Official)(_)([\d\.]+)(.zip)", r"\2\5\6\7"],

    # zeal-portable-0.6.1-windows-x64.zip
    [r"(zeal)(-portable)(-)([\d\.]+)(-windows-x64)(.zip)", (r"\1_\4\6", _capitalize_)],

]

config_python = [
    # pattern.cpython-37.pyc
    [r"(\w+)(\.cpython-37)(\.pyc)", r"\1\3"],
    # python-x.x.x.exe
    [r"(python)(-)([\d\.]+)(.exe)", (r"\1\2\3-win32\4", _capitalize_)],
    # python-x.x.x-amd64.exe
    [r"(python)(-)([\d\.]+)(-amd64)(.exe)", (r"\1\2\3\4\5", _capitalize_)],
    # python-x.x.x-embed-amd64.zip
    [r"(python)(-)([\d\.]+)(-embed)(-amd64)(.zip)", (r"\1\2\3\5\4\6", _capitalize_)],
    # python-3.9.9-embed-win32.zip
    [r"(python)(-)([\d\.]+)(-embed)(-win32)(.zip)", (r"\1\2\3\5\4\6", _capitalize_)],
]

# 替换规则
# 函数 \ 正则表达式
config_other = [

    # 下载的动漫
    # nicotv,

    bilibili,

    bdfilm,

    # MuMu20210129215157.png
    [r"(MuMu)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.png)", r"\2-\3-\4 \5-\6-\7\8"],

    # PowerToysSetup-0.36.0-x64.exe
    [r"(PowerToys)(Setup-)([\d\.]+)(-x64)(.exe)", r"\1_\3\5"],

    # xxx(无修).mp4
    [r"(.*)(\(无修\))([\.\w\d]+)", (r"\1\3")],

    # stylish-2021_12_3.json,.bin,.dms
    [r"(stylish)(-)(\d+)(_)(\d+)(_)(\d+)(.json)(,.bin,.dms)", (r"\1_\3-\5-\7\8", _capitalize_)],

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

config = config_software + config_python + config_image_video + config_other
