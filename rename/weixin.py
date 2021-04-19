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
    # wx_camera_1616986022655.jpg
    if "wx_camera_" not in item:
        return
    item = item.replace("wx_camera_", "")
    _name_, _type_ = item.split('.')
    _name_ = _name_[:-3]
    _name_ = int(_name_)
    _name_ = datetime.fromtimestamp(_name_)
    _name_ = _name_.strftime("%Y-%m-%d %H-%M-%S")
    item = f"{_name_}.{_type_}"
    return item


if __name__ == "__main__":
    rename = Rename()
    rename.folder = os.getcwd()
    rename.rule = rule
    rename.init()
    rename.command()
    rename.print()
    rename.start()
