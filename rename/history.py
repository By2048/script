import os
import sys
from datetime import datetime

try:
    from tool.rename import Rename
except ImportError:
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(path)
    from tool.rename import Rename


def need_rename(item):
    result = "Screenshot_" in item
    return result


def get_name(item):
    item = item.replace("Screenshot_", "")
    _name_, _type_ = item.split('.')
    _name_ = datetime.strptime(_name_, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H-%M-%S")
    item = f"{_name_}.{_type_}"
    return item


def main():
    rename = Rename()
    rename.folder = "R:\\History\\"
    rename.function_need_rename = need_rename
    rename.function_get_name = get_name
    rename.init()
    rename.command()
    rename.print()
    rename.start()


if __name__ == "__main__":
    main()
