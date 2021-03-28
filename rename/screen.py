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
    result = "screenshot_" in item
    return result


# screenshot_1616779141888.png
# 1616779141888 为时间戳
# 1616779141 -> 2021-03-27 01:19:01
#        888 -> 毫秒

def get_name(item):
    item = item.replace("screenshot_", "")
    _name_, _type_ = item.split('.')
    _name_ = _name_[:-3]
    _name_ = int(_name_)
    _name_ = datetime.fromtimestamp(_name_)
    _name_ = _name_.strftime("[%Y-%m-%d][%H-%M-%S]")
    item = f"{_name_}[Phone].{_type_}"
    return item


def main():
    rename = Rename()
    rename.folder = "R:\\Screens\\"
    rename.function_need_rename = need_rename
    rename.function_get_name = get_name
    rename.init()
    rename.command()
    rename.print()
    rename.start()


if __name__ == "__main__":
    main()
