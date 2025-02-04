from datetime import datetime

from pathlib import WindowsPath


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

    # VID_20241204_131511.mp4
    # VID_20240717_103322_970.mp4
    [r"(VID_)(\d{4})(\d{2})(\d{2})(_)(\d{2})(\d{2})(\d{2})(_\d{3}?)(.mp4)",
     r"\2-\3-\4_\6-\7-\8\10"],

    # Recorder_20210903135016.mp4
    [r"(Recorder_)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.mp4)",
     r"\2-\3-\4_\5-\6-\7\8"],

]