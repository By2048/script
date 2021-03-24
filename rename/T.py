import re
import os
import sys

try:
    from tool.rename import Rename
except ImportError:
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(path)
    from tool.rename import Rename

# 替换规则
config = [

    # Xftp-7.0.0063p.exe
    [r"(Xftp)(-)([\d\.]+)(\w)(.exe)", r"\1_\3\5"],

    # Xshell-7.0.0063p.exe
    [r"(Xshell)(-)([\d\.]+)(\w)(.exe)", r"\1_\3\5"],

    # ventoy-1.0.38-windows.zip
    [r"(ventoy)(-)([\d\.]+)(-windows)(.zip)", r"\1_\3\5", lambda x: x.capitalize()],

    # Screenshot_20210318215042.png
    [r"(Screenshot_)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.png)", r"\2-\3-\4 \5-\6-\7\8"],

    # FreeFileSync_11.8_Windows_Setup.exe
    [r"(FreeFileSync_)([\d+\.]+)(_Windows_Setup)(.exe)", r"\1\2\4"],

    # python-3.8.5.exe
    [r"(python)(-)([\d\.]+)(.exe)", r"\1_\3\4", lambda x: x.capitalize()],
    # python-3.9.2-amd64.exe
    [r"(python)(-)([\d\.]+)(-amd64)(.exe)", r"\1_\3\5", lambda x: x.capitalize()],

    # DG5411178_x64.zip
    [r"(DG)(\d+)(_x64)(.zip)", r"DiskGenius_\2\4"],

    # Everything-1.4.1.1005.x64.zip
    [r"(Everything)(-)([\d\.]+)(.x64)(.zip)", r"\1_\3\5"],
    # Everything-1.4.1.1005.x64-Setup.exe
    [r"(Everything)(-)([\d\.]+)(.x64-Setup)(.exe)", r"\1_\3\5"],

    # ScreenToGif.2.27.3.Setup.msi
    [r"(ScreenToGif)(\.)([\d\.]+)(.Setup)(.msi)", r"\1_\3\5"],
    # ScreenToGif.2.27.3.Portable.zip
    [r"(ScreenToGif)(\.)([\d\.]+)(.Portable)(.zip)", r"\1_\3\5"],

    # Git-2.31.0-64-bit.exe
    [r"(Git)(-)([\d\.]+)(-64-bit)(.exe)", r"\1_\3\5"],
    # PortableGit-2.31.0-64-bit.7z.exe
    [r"(Portable)(Git)(-)([\d\.]+)(-64-bit)(.7z)(.exe)", r"\2_\4\6\7"],

    # Q-Dir_Portable_x64.zip
    [r"(Q-Dir)(_)(Portable_x64)(.zip)", r"\1\4"],
    # Q-Dir_x64.exe
    [r"(Q-Dir)(_)(x64)(.exe)", r"\1\4"],

    # VMware-workstation-full-16.1.0-17198959.exe
    [r"(VMware)(-workstation-full-)([\d+\.]+)(-)(\d+)(.exe)", r"\1_\3.\5\6"],

    # FoxmailSetup_7.2.20.273.exe
    [r"(Foxmail)(Setup)(_)([\d\.]+)(.exe)", r"\1\3\4\5"],

]


def need_rename(item):
    for cfg in config:
        rule_match = cfg[0]
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
    args = sys.argv
    folder = "t:\\"
    if len(args) > 1:
        folder = args[-1]
        folder = os.getcwd() if folder == "." else folder
    rename = Rename()
    rename.folder = folder
    rename.function_need_rename = need_rename
    rename.function_get_name = get_name
    rename.init()
    rename.print()
    rename.start()
