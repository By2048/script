from pathlib import WindowsPath

from hanziconv import HanziConv


def change_name(file: WindowsPath | str) -> WindowsPath | str:
    """ 简繁转换 替换不支持的特殊符号 """
    if not file:
        return file

    new_name = file

    if isinstance(file, WindowsPath):
        new_name = file.name
    elif isinstance(file, str):
        new_name = file

    codes = [
        ('?', '？'),
        (',', '，'),

        (':', '-'),

        ('<', '['),
        ('>', ']'),
        ('【', '['),
        ('】', ']'),

        ('\\', ''),
        ('/', ''),
        ('|', ''),
        ('*', ''),
    ]
    for item in codes:
        new_name = new_name.replace(item[0], item[1])
    try:
        new_name = HanziConv.toSimplified(new_name)
    except ImportError:
        pass
    finally:
        if isinstance(file, WindowsPath):
            file = file.with_name(new_name)
            return file
        elif isinstance(file, str):
            return new_name
        return file