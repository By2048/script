import os
import re
import sys

try:
    from tool.rename import Rename
except ImportError:
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(path)
    from tool.rename import Rename


def rule(item):
    if not re.match(r"第([\d\\.]+)集", item):
        return
    item = item.replace("(无修)", "")
    data = re.match(r"(第)([\d\\.]+)(集)", item)
    item_name = data.group(2)
    item_name = item_name.zfill(2)
    item_type = item.split('.')[-1]
    return f"{item_name}.{item_type}"


if __name__ == '__main__':
    rename = Rename()
    rename.folder = os.getcwd()
    rename.rule = rule
    rename.init()
    rename.command()
    rename.print()
    rename.start()
