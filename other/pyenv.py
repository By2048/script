import os
import re
import sys
import time
from pathlib import Path

import fire
from rich import print
from rich.pretty import pprint

folder = "D:\\Python\\"
jx = "https://pypi.tuna.tsinghua.edu.cn/simple"
requirements = Path("E:\\Project\\_pip_\\requirements.txt")

pythons = []
for item in Path(folder).iterdir():
    if re.match(r"^(\d)(\.)(\d+)(.)(\d+)$", item.name):
        pythons.append(item.name)


def show():
    for item in Path(folder).iterdir():
        if item.name.endswith(".ini"):
            continue
        print(item.name)


def create(source, target):
    """ 创建环境
    @param source: 原始环境
    @param target: 目标环境
    @return:
    """

    path_target = Path(f"{folder}\\{target}")

    if source not in pythons:
        print("[red]ERROR : source not in pythons")
        print(f"[green] source = {source}")
        print(f"[green]pythons = {pythons}")
        return

    if re.match(r"^(\d)(\.)(\d+)(.)(\d+)$", target):
        print(f"[red]ERROR : target name = {target}")
        return

    if not path_target.exists():
        path_target.mkdir(parents=True, exist_ok=True)

    command = fr"""

    {folder}\{source}\python.exe -m pip install --upgrade pip -i {jx}
    {folder}\{source}\Scripts\pip.exe install virtualenv --upgrade -i {jx}、
    {folder}\{source}\Scripts\virtualenv.exe {folder}\{target}\ --python={folder}\{source}\python.exe
    
    {folder}\{target}\Scripts\pip.exe install -r {requirements} -i {jx}

    """
    command = command.replace("\\\\", "\\")
    command = command.strip()

    for cmd in command.split("\n"):
        cmd = cmd.strip()
        if not cmd:
            continue
        print(cmd)
        os.system(cmd)
        print()
        print()
        print()


def activate(target):
    command = fr"{folder}\{target}\Scripts\activate.ps1"
    command = command.replace("\\\\", "\\")
    command = command.strip()
    os.system(command)


def delete(target):
    path_target = Path(f"{folder}\\{target}")
    path_target.rmdir()
    print(f"delete {path_target}")


if __name__ == '__main__':
    fire.Fire()
