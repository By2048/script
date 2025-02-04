import re
from datetime import datetime
from functools import partial
from pathlib import WindowsPath

from .base import timestamp, timestamp_with_x
from .base import md5
from .base import zfill

# 1638862702756.jpg
timestamp_image = partial(timestamp_with_x, xxx="")

# screenshot_1616779141888.png
app_screenshot = partial(timestamp_with_x, xxx="screenshot_")

# wx_camera_1616986022655.jpg
wx_camera = partial(timestamp_with_x, xxx="wx_camera_")

# mmexport1641361625029.png
wx_image = partial(timestamp_with_x, xxx="mmexport")


def lol(file: WindowsPath):
    # 11-18_HN16_NEW-1449121099_05.webm
    if '_HN' in file.name and '_NEW' in file.name and file.name.endswith('.webm'):
        date = file.stat().st_ctime
        date = datetime.fromtimestamp(date).strftime("%Y-%m-%d_%H-%M-%S")
        file = file.with_stem(f"LOL {date}")
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


config_media = [

    # Xxxx-Xx-Xx_Xx-Xx-Xx.Xxx

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
    [r"(\d{4})(\d{2})(\d{2})(_?)(\d{2})(\d{2})(\d{2})(.jpg|.png)",
     r"\1-\2-\3_\5-\6-\7\8"],

    # 20240414_033129.jpg
    [r"(\d{4}\d{2}\d{2})(_)(\d{2}\d{2}\d{2})(.\w+)", r"\1_\3\4"],

    # 2020010214432637.png
    # 20200102144326376.png
    [r"(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2}|\d{3})(.jpg|.png)",
     r"\1-\2-\3_\4-\5-\6\8"],

    # 2019-04-01 23-15-24.jpg
    [r"(\d{4}\-\d{2}\-\d{2})( )(\d{2}\-\d{2}\-\d{2})(.\w+)", r"\1_\3\4"],

    # tumblr_ondeipvf8D1ttxriho1_1280
    [r"(tumblr_)([\d\w]+)(.\w+)", md5],

    # image_7908280.png
    [r"(image_)(\d+)(.\w+)", md5],

    # 1686050553516.jpeg.png
    [r"([\d\w]+)(.(jpg|png|jpeg|webp))(.(jpg|png|jpeg|webp))", r"\1\3"],

    # image-1686654513477.png
    [r"(image-)([\d\w]+)(.\w+)", r"\2\3"],

    # www.zhihu.com_question_628603865_answer_3272866674.png
    [r"(www.zhihu.com)(_question_)(\d+)(_answer_)(\d+)(.png|.jpg)", r"ZhiHu_\3_\5\6"],
    # www.zhihu.com_question_629230874.png
    [r"(www.zhihu.com)(_question_)(\d+)(.png|.jpg)", r"ZhiHu_\3\4"],

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
    # [r"([\d\w]+)(_\d+)(_\d{4}\d{2}\d{2}_\d{6})(.\w+)", r"\1\2\4"],
    # 109094951_p0.jpg
    # [r"(\d+)(_p0)(.\w+)", r"\1\3"],
    # 105178146_20230616_172808
    # [r"(\d+)(_)(\d+)(_)(\d+)(0)(.\w+)", r"\1\2\3\4\5\6\7"],

    # 34452206_107644944_p0.png
    # [r"(\d+_\d+)(_p0)(\.\w+)", r"\1\3\4"],
    # 34452206_107644944_0.png
    # [r"(\d+_\d+)(_p?)(0)(\.\w+)", r"\1\3\4"],

    # Screenshot_20210318215042.png
    [r"(Screenshot_|screenshot_)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.png|.jpg)",
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

    # IMG_20240624_102657_525.jpg
    [r"(IMG_)(\d{4})(\d{2})(\d{2})(_)(\d{2})(\d{2})(\d{2})(_)(\d+)(.)(jpg)",
     r"\2-\3-\4_\6-\7-\8_\10.\12"],

    # infinity-2445168.jpg
    [r"(infinity)(-)(\d+)(.jpg|.png)", md5]

]