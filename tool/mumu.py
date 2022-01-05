import os
import re
import sys
import shutil
from pathlib import WindowsPath

from rich import print

try:
    from tool.rename import Rename
except ImportError:
    sys.path.append(WindowsPath(__file__).parents[1].as_posix())
    from tool.rename import Rename

path_from = WindowsPath("C:\\Users\\Administrator\\Documents\\MuMu共享文件夹\\")
path_to = WindowsPath("P:\\Image\\Android\\")

files_from = []


def rule(file: WindowsPath) -> WindowsPath:
    # MuMu20210129215157.png
    _match_ = r"(MuMu)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(.png)"
    _get_ = r"\2-\3-\4 \5-\6-\7\8"
    if not re.match(_match_, file.name):
        return file
    new_name = re.sub(_match_, _get_, file.name)
    file = file.with_name(new_name)
    return file


if not path_from.exists():
    print()
    print(f"[red]Not Exists[/red] : {path_from}")
    print()
    exit()

print()

rename = Rename()
rename.folder = path_from
rename.rule = rule
rename.init()
rename.start(silent=True)
print(f"[red]Folder[/red] : {path_from}")

print(f"[red]Rename[/red] : ", end="" if len(rename.files) else "\n")
for index, file in enumerate(rename.files, 1):
    print(f"{'         ' if index != 1 else ''}{index} {file.old.name} -> {file.new.name}")

for file in path_from.iterdir():
    files_from.append(file)
    shutil.move(file, path_to)
print(f"[red]Move[/red]   : {path_from} -> {path_to}")

shutil.rmtree(path_from)
print(f"[red]Delete[/red] : {path_from}")

print()
