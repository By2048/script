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
    from tool.rename import Rename, get_version
except ImportError:
    sys.path.append(WindowsPath(__file__).parents[1].as_posix())
    from tool.rename import Rename, get_version


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


def version_x(file: WindowsPath, key: str):
    if key.lower() not in file.name.lower():
        return
    version_data = get_version(file)
    if version_data:
        new_name = f"{key}_{version_data}.exe"
    else:
        new_name = f"{key}.exe"
    file = file.with_name(new_name)
    return file


#
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


upper_1 = partial(upper_x, index=1)
upper_2 = partial(upper_x, index=2)
upper_3 = partial(upper_x, index=3)
upper_4 = partial(upper_x, index=4)
upper_5 = partial(upper_x, index=5)
upper_all = partial(upper_x, index=-1)

github = partial(version_x, key="GitHubDesktop")
potplayer = partial(version_x, key="PotPlayer")
ntlite = partial(version_x, key="NTLite")  # noqa
postman = partial(version_x, key="Postman")

# 1638862702756.jpg
timestamp_image = partial(timestamp_with_x, xxx="")

# screenshot_1616779141888.png
app_screenshot = partial(timestamp_with_x, xxx="screenshot_")

# wx_camera_1616986022655.jpg
wx_camera = partial(timestamp_with_x, xxx="wx_camera_")

# mmexport1641361625029.png
wx_image = partial(timestamp_with_x, xxx="mmexport")


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


def lol(file: WindowsPath):
    # 11-18_HN16_NEW-1449121099_05.webm
    if '_HN' in file.name and '_NEW' in file.name and file.name.endswith('.webm'):
        date = file.stat().st_ctime
        date = datetime.fromtimestamp(date).strftime("%Y-%m-%d_%H-%M-%S")
        file = file.with_stem(f"LOL {date}")
        return file


def app_screen(file: WindowsPath):
    # Chrome_1618427487075.png
    # 1616779141888 为时间戳
    # 1616779141 -> 2021-03-27 01:19:01
    #        888 -> 毫秒
    if "_" in file.name and "-" not in file.name:
        _app_, _date_ = file.stem.split("_")
        if len(_date_) != 13 or len(_app_) <= 0:
            return
        _date_ = _date_[:-3]
        _date_ = int(_date_)
        _date_ = datetime.fromtimestamp(_date_)
        _date_ = _date_.strftime("[%Y-%m-%d][%H-%M-%S]")
        file = file.with_stem(f"{_date_}[{_app_}]")
        return file


def nicotv(file: WindowsPath):
    if not re.match(r"第([\d\\.]+)集", file.stem):
        return
    file.stem = file.stem.replace("(无修)", "")
    data = re.match(r"(第)([\d\\.]+)(集)", file.stem)
    item_stem = data.group(2)
    item_stem = item_stem.zfill(2)
    file = file.with_stem(item_stem)
    return file


def bilibili(file: WindowsPath):
    if ".mp4" not in file.name or "Av" not in file.name:
        return

    info = file.name.split('.')
    try:
        index = info[0].zfill(2)
        name = info[1]
        file_type = info[2]
    except Exception as e:
        print(f'\n文件名解析错误 {file.name}\n')
        return

    name = re.split(r'\([avAVpP,\d]+\)', name)  # 去除(Avxxxxxx,Px)
    name = [item for item in name if bool(item)]
    name = ''.join(name)
    name = name.rstrip("_ ")
    new_stem = f"{index} {name}"
    file = file.with_stem(new_stem)
    return file


def bdfilm(file: WindowsPath):
    if "bd2020" not in file.name:
        return

    name = file.name
    name = name.replace("[BD影视分享bd2020.com]", "")
    name = name.replace("[BD影视分享bd2020.co]", "")
    name = name.replace("mp41", "mp4")
    name = name.strip()
    name = name.replace(':', ' ')
    name = name.replace('：', ' ')

    file = file.with_name(name)
    return file


def md5(file: WindowsPath):
    hash_md5 = hashlib.md5()
    with open(file, "rb") as content:
        while chunk := content.read(4096):
            hash_md5.update(chunk)
    hash_md5 = hash_md5.hexdigest()
    file = file.with_stem(hash_md5)
    return file


def record(file: WindowsPath):
    # 9月29日 23点58分.mp3
    name = file.name.lower()
    data = "月,日,点,分".split(",")
    check = True
    for item in data:
        if item not in name:
            check = False
    if not check:
        return

    stem = file.stem.replace(" ", "")
    for item in data:
        stem = stem.replace(item, " ")

    stem = stem.split(" ")
    year = datetime.now().year
    month = stem[0].zfill(2)
    day = stem[1].zfill(2)
    hour = stem[2].zfill(2)
    minute = stem[3].zfill(2)

    stem = f"{year}-{month}-{day} {hour}-{minute}"
    file = file.with_stem(stem)
    return file


config_phone = [

    # 通话录音
    record,

    # 950618(950618)_20210627205223.mp3
    # 15669947201(15669947201)_20211015170939.mp3
    #  1        2   3    4   5  6      7      8      9      10     11     12
    [r"([\s\S]+)(\()(\d+)(\))(_)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.mp3)",
     r"(\6-\7-\8)(\9-\10-\11)(\3)(\1)\12"],

    # 9月29日 23点58分.mp3
    #  1    2   3    4   5    6   7   8   9    10
    # [r"(\d+)(月)(\d+)(日)(\s+)(\d+)(点)(\d+)(分)(.mp3)", r"\1-\3-\6-\8\10"],

    # setting_backup_20220318131853.zip
    [r"(setting_backup_)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.zip)",
     r"FooViewConfig_\2-\3-\4_\5-\6-\7\8"],

    # VID_20210731_144747.mp4
    [r"(VID_)(\d{4})(\d{2})(\d{2})(_)(\d{2})(\d{2})(\d{2})(.mp4|.3gp)",
     r"\2-\3-\4_\6-\7-\8\9"],

    # Recorder_20210903135016.mp4
    [r"(Recorder_)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.mp4)",
     r"\2-\3-\4_\5-\6-\7\8"],

]

config_media = [

    # 微信保存的图片
    wx_camera,
    wx_image,

    lol,

    # 手机屏幕截图
    app_screen,
    app_screenshot,

    timestamp,
    timestamp_image,

    # 下载的动漫
    # nicotv,

    bilibili,

    bdfilm,

    # 第1集
    # 第xxx集
    [r"(第)(\d+)(集|话)(\s)(\S+)", (r"\2 \5", zfill)],
    [r"(第)(\d+)(集|话)([\.\w\d]+)", (r"\2\4", zfill)],

    # xxx(无修).mp4
    [r"(.*)(\(无修\))([\.\w\d]+)", (r"\1\3")],

    # MuMu20210129215157.png
    [r"(MuMu)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.png)",
     r"\2-\3-\4_\5-\6-\7\8"],

    # PANO_20140629_080915.jpg
    [r"(PANO_)(\d{4})(\d{2})(\d{2})(_)(\d{2})(\d{2})(\d{2})(.jpg)",
     r"\2-\3-\4_\6-\7-\8\9"],

    # 20210622183532.jpg
    [r"(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.jpg|.png)",
     r"\1-\2-\3_\4-\5-\6\7"],

    # 2020010214432637.png
    # 20200102144326376.png
    [r"(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2}|\d{3})(.jpg|.png)",
     r"\1-\2-\3_\4-\5-\6\8"],

    # 2019-04-01 23-15-24.jpg
    [r"(\d{4}\-\d{2}\-\d{2})( )(\d{2}\-\d{2}\-\d{2})(.\w+)", r"\1_\3\4"],

    # tumblr_ondeipvf8D1ttxriho1_1280
    [r"(tumblr_)([\d\w]+)(.\w+)", md5],

    # 1686050553516.jpeg.png
    [r"([\d\w]+)(.(jpg|png|jpeg|webp))(.(jpg|png|jpeg|webp))", r"\1\3"],

    # 109094951_p0.jpg
    [r"(\d+)(_p0)(.\w+)", r"\1\3"],
    # 34452206_107644944_0.png
    [r"(\d+_\d+)(_p?)(0)(\.\w+)", r"\1\3\4"],

    # image-1686654513477.png
    [r"(image-)([\d\w]+)(.\w+)", r"\2\3"],

    # 1638862702.jpg
    # 1638862702756.jpg
    # ".png .jpg .jpeg .gif .webm"
    # len(_stem_) in [13, 10]:

    # v2-48fa5b6760cfe078212498c6667a77a0.jpeg
    [r"(v2-)([\d\w]{30,})(.jpeg|.jpg|.png|.webp)", md5],

    # 93e7a7c89561987d20b7e322f5c5882644714970.jpg
    [r"([\d\w]{35,})(.jpeg|.jpg|.png|.webp)", md5],

    # Pixiv下载
    # illust_105178146_20230616_172808.jpg
    [r"([\d\w]+)(_\d+)(_\d{4}\d{2}\d{2}_\d{6})(.\w+)", r"\1\2\4"],

    # Screenshot_20210318215042.png
    [r"(Screenshot_)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.png)",
     r"\2-\3-\4_\5-\6-\7\8"],

    # Screenshot_2014-08-31-13-59-51.png
    [r"(Screenshot_)(\d{4}\-\d{2}\-\d{2})(\-)(\d{2}\-\d{2}\-\d{2})(.png)", r"\2 \4\5"],

    # Screenshot_2013-11-29-13-01-53-1.png
    [r"(Screenshot_)(\d{4}\-\d{2}\-\d{2})(\-)(\d{2}\-\d{2}\-\d{2})(\-1)(.png)",
     r"\2_\4\6"],

    # IMG20200712095720.jpg
    # IMG_20200712095720.jpg
    # IMG_2022111281528.jpg
    [r"(IMG|IMG_)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.jpg)",
     r"\2-\3-\4_\5-\6-\7\8"],

    # QQ图片xxx.jpg
    [r"(QQ图片)([\d\w]+)(.jpeg|.jpg|.png|.webp)", md5],

    # IMG_20200926_214521.jpg
    [r"(IMG_)(\d{4})(\d{2})(\d{2})(_)(\d{2})(\d{2})(\d{2})(.jpg)",
     r"\2-\3-\4_\6-\7-\8\9"],

    # IMG_2013-10-05_22.23.51.jpg
    [r"(IMG_)(\d{4}-\d{2}-\d{2})(_)(\d{2})(\.)(\d{2})(\.)(\d{2})(.jpg)",
     r"\2_\4-\6-\8\9"],

    # IMG_20040622_141354_HDR.jpg
    [r"(IMG_)(\d{4})(\d{2})(\d{2})(_)(\d{2})(\d{2})(\d{2})(_HDR)(.jpg)",
     r"\2-\3-\4_\6-\7-\8\10"],

    # infinity-2445168.jpg
    [r"(infinity)(-)(\d+)(.jpg|.png)", md5]

]

config_software = [

    github,
    potplayer,
    ntlite,
    postman,

    # Xftp-7.0.0063p.exe
    [r"(Xftp)(-)([\d\.]+)(\w)(.exe)", r"\1_\3\5"],

    # Xshell-7.0.0063p.exe
    [r"(Xshell)(-)([\d\.]+)(\w)(.exe)", r"\1_\3\5"],

    # ideaIU-2023.2.exe
    # pycharm-professional-2023.2.exe
    [r"(ideaIU)(-)([\d\.]+)(.exe)", r"IDEA_\3\4"],
    [r"(pycharm-professional)(-)([\d\.]+)(.exe)", r"PyCharm_\3\4"],

    # aria2-1.36.0-win-64bit-build1.zip
    [r"(aria2)(-)([\d\.]+)(-win-64bit-build1)(.zip)", (r"\1_\3\5", capitalize)],

    # dexpot_1614_portable_r2439.zip
    [r"(dexpot)(_)([\d\.]+)(_portable)(\_\w+)(.zip)", (r"\1_\3\6", capitalize)],
    # dexpot_1614_r2439.exe
    [r"(dexpot)(_)([\d\.]+)(\_\w+)(.exe)", (r"\1_\3\5", capitalize)],

    # ventoy-1.0.38-windows.zip
    [r"(ventoy)(-)([\d\.]+)(-windows)(.zip)", r"Ventoy_\3\5"],
    # iventoy-1.0.08-win64.zip
    [r"(iventoy)(-)([\d\.]+)(-win64)(.zip)", r"VentoyI_\3\5"],

    # BitComet_1.87_setup.exe
    [r"(BitComet)(_)([\d\.]+)(_setup)(.exe)", r"\1_\3\5"],

    # BCompare-zh-4.4.6.27483.exe
    [r"(BCompare)(-zh-)([\d\.]+)(.exe)", r"\1_\3\4"],

    # ffmpeg-2021-12-12-git-996b13fac4-full_build.7z
    [r"(ffmpeg)(-)([\d\-]+)(-)(git\-\w+)(\-full_build)(.7z)", (r"\1_\3\7", upper_2)],
    # ffmpeg-5.1.2-essentials_build.7z
    [r"(ffmpeg)(-)([\d\.]+)(-essentials_build)(.7z)", (r"\1_\3\5", upper_2)],

    # navicat150_premium_cs_x64.exe
    [r"(navicat)([\d]+)(_premium_cs_x64)(.exe)", (r"\1_\2\4", capitalize)],

    # cloudmusicsetup2.9.5.199424.exe
    [r"(cloudmusic)(setup)([\d\.]+)(.exe)", r"CloudMusic_\3\4"],

    # scrcpy-win64-v1.24.zip
    [r"(scrcpy)(-win64)(-v)([\d\.]+)(.zip)", r"Scrcpy_\4\5"],

    # rdm-2021.3.0.0.exe
    # resp-2022.3.0.0.exe
    [r"(rdm|resp)(-)([\d\.]+)(.exe)", (r"\1_\3\4", upper_all)],

    # QuiteRSS-0.19.4.zip
    [r"(QuiteRSS)(-)([\d\.]+)(.zip)", r"\1_\3\4"],

    # MobaXterm_Portable_v22.0.zip
    [r"(MobaXterm)(_Portable_)(v)([\d\.]+)(.zip)", r"\1_\4\5"],

    # FreeFileSync_11.8_Windows_Setup.exe
    [r"(FreeFileSync_)([\d\.]+)(_Windows_Setup)(.exe)", r"\1\2\4"],

    # SumatraPDF-3.3.3-64.zip  portable (zip) v
    [r"(SumatraPDF)(\-)([\d\.]+)(-64)(\.zip)", r"\1_\3_Portable\5"],
    # SumatraPDF-3.3.3-64-install.exe
    [r"(SumatraPDF)(\-)([\d\.]+)(-64)(-install)(\.exe)", r"\1_\3_Install\6"],

    # sysdiag-all-5.0.64.2-2021.11.3.1.exe
    [r"(sysdiag)(\-all\-)([\d\.]+)(\-)([\d\.]+)(.exe)", r"HuoRong_\3\6"],

    # WiresharkPortable_3.4.9.paf.exe
    [r"(Wireshark)(Portable|Portable64)(_)([\d\.]+)(.paf)(.exe)", r"\1_\4\6"],

    # node-v14.17.0-win-x64.zip
    [r"(node)(-v)([\d\.]+)(-win-x64)(.zip)", (r"\1_\3\5", capitalize)],

    # DG5411178_x64.zip
    [r"(DG)(\d+)(_x64)(.zip)", r"DiskGenius_\2\4"],

    # Everything-1.4.1.1005.x64.zip
    [r"(Everything)(-)([\d\.]+)(.x64)(.zip)", r"\1_\3\5"],
    # Everything-1.4.1.1005.x64-Setup.exe
    [r"(Everything)(-)([\d\.]+)(.x64-Setup)(.exe)", r"\1_\3\5"],

    # ScreenToGif.2.27.3.Setup.msi
    [r"(ScreenToGif)(\.)([\d\.]+)(.Setup)(.msi)", r"\1_\3\5"],
    # ScreenToGif.2.27.3.Portable.zip
    [r"(ScreenToGif)(\.)([\d\.]+)(.Portable|.Portable.x64)(.zip)", r"\1_\3\5"],

    # Git-2.31.0-64-bit.exe
    [r"(Git)(-)([\d\.]+)(-64-bit)(.exe)", r"\1_\3\5"],
    # PortableGit-2.31.0-64-bit.7z.exe
    [r"(Portable)(Git)(-)([\d\.]+)(-64-bit)(.7z)(.exe)", r"\2_\4\6\7"],

    # platform-tools_r33.0.3-windows.zip
    [r"(platform-tools)(_r)([\d\.]+)(-windows)(.zip)", r"Adb_\3\5"],

    # Q-Dir_Portable_x64.zip
    [r"(Q-Dir)(_)(Portable_x64)(.zip)", r"\1\4"],
    # Q-Dir_Portable_x64_9.97.zip
    [r"(Q-Dir)(_)(Portable_x64)(_)([\d\.]+)(.zip)", r"\1\2\5\6"],
    # Q-Dir_x64.exe
    [r"(Q-Dir)(_)(x64)(.exe)", r"\1\4"],

    # calibre-portable-installer-5.32.0.exe
    [r"(calibre)(-portable-installer-)([\d\.]+)(.exe)", (r"\1_\3\4", capitalize)],

    # VSCodeSetup-x64-1.61.2.exe
    [r"(VSCode)(Setup)(-x64-)([\d\.]+)(.exe)", r"\1_\4\5"],

    # AutoHotkey_1.1.33.10_setup.exe
    [r"(AutoHotkey)(_)([\d\.]+)(_setup)(.exe)", r"\1_\3\5"],
    # AutoHotkey_2.0-beta.3.zip
    [r"(AutoHotkey)(_)([\d\.]+)(-beta)([\d\.]+)(.zip)", r"\1_\3\5\6"],

    # Maye.1.2.6-20211001.zip
    [r"(Maye)(.)(\d.\d.\d)(-)(\d+)(.zip)", r"\1_\3\6"],

    # VeraCrypt_1.24-Update7.zip
    [r"(VeraCrypt)(_)([\d\.]+)(-Update)(\d)(.zip)", r"\1\2\3.\5\6"],
    # VeraCrypt Setup 1.24-Update7
    [r"(VeraCrypt)( Setup )([\d\.]+)(-Update)(\d)(.exe)", r"\1_\3.\5\6"],

    # go1.17.3.windows-arm64.zip
    [r"(go)([\d\.]+)(.windows)(-amd64|-arm64)(.zip)", (r"\1_\2\5", capitalize)],

    # jdk-17_windows-x64_bin.zip
    [r"(jdk)(-)([\d\.]+)(_windows)(-x64_bin)(.zip)", (r"\1_\3\6", upper_all)],

    # frp_0.38.0_windows_amd64.zip
    [r"(frp)(_)([\d\.]+)(_windows_amd64)(.zip)", (r"\1_\3\5", capitalize)],

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
    # Xmind-for-Windows-x64bit-22.11.3656.exe
    [r"(XMind|Xmind)(-for)(-Windows-)(64bit|x64bit)(-)([\d\.]+)(.exe)", r"\1_\6\7"],

    # VSCode-win32-x64-1.75.1.zip
    # VSCodeSetup-x64-1.75.1.exe
    [r"(VSCode)(-win32-x64-)([\d\.]+)(.zip)", r"\1_\3\4"],
    [r"(VSCode)(Setup)(-x64-)([\d\.]+)(.exe)", r"\1_\4\5"],

    # FoxmailSetup_7.2.20.273.exe
    [r"(Foxmail)(Setup)(_)([\d\.]+)(.exe)", r"\1\3\4\5"],

    # MouseInc2.12.1.7z
    [r"(MouseInc)([\d\.]+)(.7z)", r"\1_\2\3"],

    # npp.8.1.9.portable.x64.zip
    [r"(npp.)([\d\.]+)(.portable)(.x64)(.zip)", r"Notepad++_\2\5"],

    # QuickLook-3.7.0.zip
    [r"(QuickLook)(-)([\d\.]+)(.zip)", r"\1_\3\4"],

    # Apifox-2.1.34.exe
    [r"(Apifox)(-)([\d\.]+)(.exe)", r"\1_\3\4"],

    # Firefox Setup 94.0.1.exe
    [r"(Firefox)(\s)(Setup)(\s)([\d\.]+)(.exe)", r"\1_\5\6"],

    # Snipaste-2.6.6-Beta-x64.zip
    [r"(Snipaste)(-)([\d\.]+)(-Beta-x64)(.zip)", r"\1_\3\5"],

    # Obsidian.0.13.19.exe
    [r"(Obsidian)(\.)([\d\.]+)(\.exe)", r"\1_\3\4"],

    # jetbrains-toolbox-1.22.10685.exe
    [r"(jetbrains)(-)(toolbox)(-)([\d\.]+)(.exe)", (r"\1_\5\6", capitalize)],

    # Samsung_Magician_Installer_Official_7.0.0.510.zip
    [r"(Samsung_)(Magician)(_Installer)(_Official)(_)([\d\.]+)(.zip)", r"\2\5\6\7"],

    # zeal-portable-0.6.1-windows-x64.zip
    [r"(zeal)(-portable)(-)([\d\.]+)(-windows-x64)(.zip)", (r"\1_\4\6", capitalize)],

    # Postman-win64-9.5.0-Setup.exe
    [r"(Postman)(-win64-)([\d\.]+)(-Setup)(.exe)", r"\1_\3\5"],

    # qbittorrent_4.4.1_x64_setup.exe
    [r"(qbittorrent)(_)([\d\.]+)(_x64_setup)(.exe)", r"QBittorrent_\3\5"],

    # chrome-win.zip
    [r"(chrome)(-)(win)(.zip)", r"Chromium.zip"],
    # chromedriver_win32.zip
    [r"(chromedriver)(_)(win32)(.zip)", r"ChromeDriver.zip"],

    # PowerShell-7.2.2-win-x64.zip
    [r"(PowerShell)(-)([\d\.]+)(-win-x64)(.zip)", r"\1_\3\5"],

    # gvim_8.2.2825_x86_signed.exe
    [r"(gvim)(_)([\d\.]+)(_x86_signed)(.exe)", r"GVim_\3\5"],

    # PowerToysSetup-0.36.0-x64.exe
    [r"(PowerToys)(Setup-)([\d\.]+)(-x64)(.exe)", r"\1_\3\5"],

    # WindTerm_2.5.0_Windows_Portable_x86_64.zip
    [r"(WindTerm_)([\d\.]+)(_Windows_Portable_x86_64)(.zip)", r"\1\2\4"],

    # OBS-Studio-29.0.1.zip
    # OBS-Studio-29.0.1-Full-Installer-x64.exe
    [r"(OBS)(-Studio-)([\d\.]+)(.zip)", r"\1_\3\4"],
    [r"(OBS)(-Studio-)([\d\.]+)(-Full-Installer-x64)(.exe)", r"\1_\3\5"],

    # LibreOffice_7.4.5_Win_x64.msi
    [r"(LibreOffice)(_)([\d\.]+)(_Win_x64)(.msi)", r"\1_\3\5"],
    # LibreOffice_7.4.5_Win_x64_sdk.msi
    [r"(LibreOffice)(_)([\d\.]+)(_Win_x64)(_sdk)(.msi)", r"\1SDK_\3\6"],

]

config_iso = [

    # manjaro-xfce-21.1.6-211017-linux513.iso
    [r"(manjaro)(-)(\w+)(-)([\d\.]+)(-)(\d+)(-linux)(\d+)(.iso)",
     r"Manjaro [version]\5 [linux]\9 [data]\7 [type]\3\10"],

    # debian-11.5.0-amd64-DVD-1.iso
    [r"(debian)(-)([\d\.]+)(-amd64-DVD-1)(.iso)", r"Debian_\3\5"],

    # debian-11.5.0-amd64-netinst.iso
    [r"(debian)(-)([\d\.]+)(-amd64-)(netinst)(.iso)", r"Debian_\3_NetInstall\6"],

    # ubuntu-18.04.6-live-server-amd64.iso
    [r"(ubuntu)(-)([\d\.]+)(-live-server-amd64)(.iso)", r"Ubuntu_Server_\3\5"],
    # ubuntu-22.04.2-desktop-amd64.iso
    [r"(ubuntu)(-)([\d\.]+)(-desktop-amd64)(.iso)", r"Ubuntu_Desktop_\3\5"],

    # deepin-desktop-community-20.8-amd64.iso
    # deepin-desktop-community-23-Alpha2-amd64.iso
    [r"(deepin)(-desktop-community-)([\d\.]+)(-amd64)(.iso)", r"Deepin_\3\5"],
    [r"(deepin)(-desktop-community-)(\d+)(-Alpha)(\d)(-amd64)(.iso)",
     r"Deepin_Alpha_\3.\5\7"],

    # kali-linux-2023.1-installer-amd64.iso
    # kali-linux-2023.1-vmware-amd64.7z
    [r"(kali)(-linux-)([\d\.]+)(-installer-amd64)(.iso)", r"Kali_\3\5"],
    [r"(kali)(-linux-)([\d\.]+)(-vmware-amd64)(.7z)", r"Kali_\3\5"],

]

config_python = [
    # pattern.cpython-37.pyc
    [r"(\w+)(\.cpython-37)(\.pyc)", r"\1\3"],
    # python-x.x.x.exe
    [r"(python)(-)([\d\.]+)(.exe)", (r"\1_\3\4", capitalize)],
    # python-x.x.x-amd64.exe
    [r"(python)(-)([\d\.]+)(-amd64)(.exe)", (r"\1_\3\5", capitalize)],
    # python-x.x.x-embed-amd64.zip
    [r"(python)(-)([\d\.]+)(-embed)(-amd64)(.zip)", (r"\1_\3\5\4\6", capitalize)],
    # python-3.9.9-embed-win32.zip
    [r"(python)(-)([\d\.]+)(-embed)(-win32)(.zip)", (r"\1_\3\5\4\6", capitalize)],
]

# 替换规则
# 函数 \ 正则表达式
config_other = [

    #  [Keep] XMind.lnk
    [r"(\[)(Keep)(\])(\s)([\d\w]+)(.lnk)", r"\1#\3\5\6"],

    # 〔98'〕
    [r"(〔)([\s\S]+)(〕)(\.\w+)",
     (r"\2\4", lambda f: f.with_name(f.name.replace("'", " ")))]

]

config_rename = [] \
                + config_phone \
                + config_media \
                + config_software \
                + config_iso \
                + config_python \
                + config_other

try:
    from config_tmp import config
except ImportError:
    from .config_tmp import config
finally:
    config = [] if not config else config
    config_rename = config + config_rename