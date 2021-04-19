import os
import sys
from datetime import datetime

try:
    from tool.rename import Rename
except ImportError:
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(path)
    from tool.rename import Rename


def rule(item):
    if "Screenshot_" not in item:
        return
    item = item.replace("Screenshot_", "")
    _name_, _type_ = item.split('.')
    _name_ = datetime.strptime(_name_, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H-%M-%S")
    item = f"{_name_}.{_type_}"
    return item


if __name__ == "__main__":
    rename = Rename()
    rename.folder = "P:\\History\\"
    rename.rule = rule
    rename.init()
    rename.command()
    rename.print()
    rename.start()
