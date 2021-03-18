import re
import os
import sys

path = "T:\\"

import os
import sys

try:
    from tool.rename import Rename
except ImportError:
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(path)
    from tool.rename import Rename

config = [
    # Xftp-7.0.0063p.exe
    [r"(Xftp)(-)(\d.\d.\d+)(\w)(.exe)", r"\1_\3\5"],

    # Xshell-7.0.0063p.exe
    [r"(Xshell)(-)(\d.\d.\d+)(\w)(.exe)", r"\1_\3\5"],

    # ventoy-1.0.38-windows.zip
    [r"(ventoy)(-)(\d.\d.\d+)(\w+)(-)(\w+)(.zip)", r"\1_\3\7", lambda x: x.title()],
]


def need_rename(item):
    for cfg in config:
        rule_match = cfg[0]
        rule_name = cfg[1]
        if re.match(rule_match, item):
            return True
    return False


def get_name(item):
    for cfg in config:
        rule_match = cfg[0]
        rule_name = cfg[1]
        rule_py = cfg[2] if len(cfg) == 3 else lambda x: x
        if re.match(rule_match, item):
            name = re.sub(rule_match, rule_name, item)
            name = rule_py(name)
            return name
    return item


if __name__ == '__main__':
    rename = Rename()
    rename.folder = "T:\\"
    rename.function_need_rename = need_rename
    rename.function_get_name = get_name
    rename.init()
    rename.print()
    rename.start()
