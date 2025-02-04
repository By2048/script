import re
from pathlib import WindowsPath

config_temp = [

    # 03 第3话 周六晚上与周日早上 CASH EYE.mp4
    [r"(\d\d )(第\d+话 )([\s\S]+)(.mp4)", r"\1\3\4"],

    # 22-00-48-image.Xxx
    [r"(\d\d-\d\d-\d\d)(\-image)(\.\w+)", r"\1\3"],

    # [r"(\(無修正\)\s+)(.*)", r"\2"],

    [r"(tumblr_)([\d\w]+?)(_r\d|_\d+)?(.mp3|.mp4|.jpg|.png)", r"\2\4"],

    # [r"(p[\d|\w])([\d\w\.]+)(1voidfzo1|2_\d+)([\d\w\.]+)", r"\2\4"],

    # Daniel Powter-Free Loop.wav
    [r"([\d\w\s]+)(\-)([\d\w\s]+)(.wav|.mp3|.flac)", r"\3 - \1\4"],

]

# [DMG&SumiSora&VCB-Studio] Engage Kiss [01][Ma10p_1080p][x265_flac].mkv
# [DMG&SumiSora&VCB-Studio] Engage Kiss [01][Ma10p_1080p].sc.ass
# [VCB-Studio] NOBUNAGA THE FOOL [01][Ma10p_1080p][x265_flac_aac].mkv
# [VCB-Studio] Kaguya-sama wa Kokurasetai？Ultra Romantic [01][Ma10p_1080p][x265_flac_2aac].mkv
# [DMG&SumiSora&VCB-Studio] Mahouka Koukou no Yuutousei [01][720p][x264_aac][cht].mp4
_match = r"(\[)(.*VCB-Studio.*)(\])" \
         r"([\d\s\S\w]+)" \
         r"(\[)(\d+)(\])" \
         r"(\[)(Ma10p_1080p|720p)(\])" \
         r"(\[)(x265_flac_aac|x265_flac|Ma10p_1080p|x265_flac_2aac|x264_aac)(\])" \
         r"(\[cht\])?" \
         r"(.jpsc|.JPSC|.sc&jp|.SC&JP|.sc|.SC|.tc|.TC)?" \
         r"(.mka|.mkv|.ass|.mp4)"
_get = r"\6\16"
config_temp.append([_match, _get])

# _match = r"(.*)" \
#          r"(\[)(\d\d)(\])" \
#          r"(.*)" \
#          r"(.mkv|.mp4)"

# _get = r"\3\6"
# config.append([_match, _get])