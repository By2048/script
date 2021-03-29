import re
import os
import sys

try:
    from tool.rename import Rename
except ImportError:
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(path)
    from tool.rename import Rename


def need_rename(item):
    # IMG_20200926_214521.jpg
    result = "IMG" in item
    return result


def get_name(item):
    # 2020-09-26 21-45-21.jpg
    rule = [
        r"(IMG_)(\d{4})(\d{2})(\d{2})(_)(\d{2})(\d{2})(\d{2})(.jpg)",
        r"\2-\3-\4 \6-\7-\8\9"
    ]
    if re.match(rule[0], item):
        item = re.sub(rule[0], rule[1], item)
    return item


def main():
    rename = Rename()
    rename.folder = "R:\\Phone\\Camera\\"
    rename.function_need_rename = need_rename
    rename.function_get_name = get_name
    rename.init()
    rename.command()
    rename.print()
    rename.start()


if __name__ == "__main__":
    main()
