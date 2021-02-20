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
    return re.match(r"第([\d\\.]+)集", item)


def get_name(item):
    item = item.replace("(无修)", "")
    data = re.match(r"(第)([\d\\.]+)(集)", item)
    item_name = data.group(2)
    item_name = item_name.zfill(2)
    item_type = item.split('.')[-1]
    return f"{item_name}.{item_type}"


def main():
    folder = os.getcwd()
    rename = Rename()
    rename.folder = folder
    rename.function_need_rename = need_rename
    rename.function_get_name = get_name
    rename.init()
    rename.print()
    rename.start()


def test():
    pass


if __name__ == '__main__':
    main()
    # test()
