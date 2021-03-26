import os
import re
import sys

try:
    from tool.rename import Rename
except ImportError:
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(path)
    from tool.rename import Rename


def need_rename(item):
    return ".mp4" in item and "Av" in item


def get_name(item):
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


if __name__ == '__main__':
    rename = Rename()
    rename.folder = os.getcwd()
    rename.function_need_rename = need_rename
    rename.function_get_name = get_name
    rename.init()
    rename.print()
    rename.start()
