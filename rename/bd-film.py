import os
import sys

try:
    from tool.rename import Rename
except ImportError:
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(path)
    from tool.rename import Rename


def need_rename(item):
    result = "bd-film.cc" in item or "bd2020" in item
    return result


def get_name(item):
    name = item.replace("[BD影视分享bd-film.cc]", "")
    name = name.replace("[BD影视分享bd2020.com]", "")
    name = name.strip()
    name = name.replace(':', ' ')
    name = name.replace('：', ' ')
    _name_, *_, _type_ = name.split('.')
    _type_ = _type_.replace("mp41", "mp4")
    return f"{_name_}.{_type_}"


if __name__ == '__main__':
    rename = Rename()
    rename.folder = os.getcwd()
    rename.function_need_rename = need_rename
    rename.function_get_name = get_name
    rename.init()
    rename.print()
    rename.start()
