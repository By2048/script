import json
import os
import sys
import time
import math
import subprocess
import builtins
import re

import rich.padding
from rich import *
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.panel import Panel
from rich.progress import SpinnerColumn, Progress, BarColumn, TextColumn
from rich.table import Table
from rich.layout import Layout
from rich.console import Console
from rich.console import Group
from rich.live import Live
from rich import box
from rich import print as rprint
from rich import get_console

from pathlib import WindowsPath

console = rich.console.Console()

w = 140
h = 28
# if console.width < w or console.height < h:
#     rprint(f"Console {console.width}x{console.height}")
#     exit()
x = int((console.width - w) / 2)
y = int((console.height - h) / 2)

layout = Layout()

# cmd = r"D:\Git\bin\git.exe clone --progress git@github.com:By2048/script.git"
# cmd = r"D:\Git\bin\git.exe clone --progress https://github.com/fatedier/frp.git"


folder = WindowsPath(r"E:\\GitX\\")
folder_paths = list(folder.iterdir())
folder_names = [item.name for item in folder_paths]

page_size = 20
folder_pages = []
for i in range(0, len(folder_paths), page_size):
    folder_pages.append(folder_paths[i:i + page_size])
page_total = len(folder_pages)


def update_table_tree(path: WindowsPath):
    table = Table(box=None, padding=0, show_footer=False, show_header=False,
                  title=f"{folder}\\", title_style="white",
                  caption=f"1 / {page_size}", caption_style="white")
    table.add_column(justify="left", width=2)
    table.add_column(width=1)
    table.add_column(justify="left", width=28)

    table.add_row("", "", "")

    page_index = 0
    folder_page = []
    check = False
    for page_item in folder_pages:
        page_index += 1
        for item in page_item:
            if item == path:
                folder_page = page_item
                check = True
                break
        if check:
            break

    for index, value in enumerate(folder_page, start=1):
        if path == value:
            table.add_row(str(index).zfill(2), "", value.name, style="Black On White")
        else:
            table.add_row(str(index).zfill(2), "", value.name)

    if offset := page_size - len(table.rows):
        for _ in range(0, offset + 1):
            table.add_row("", "", "")

    table.caption = f"{page_index} / {page_total}"

    table.add_row("", "", "")
    layout["Folder"].update(Panel(table))


def update_git_remote(path: WindowsPath):
    command = r"D:\Git\bin\git.exe remote -v"
    proc = subprocess.run(command, cwd=path, capture_output=True)
    result = proc.stdout.decode("gbk")
    re_data = re.search(r"(origin\t|\s)((http|git)(.*)(\.git))(\t|\s\(fetch\))", result)
    if not re_data:
        raise Exception("Git Url Error")
    url = re_data.group(2).strip()
    git_url = Panel(
        Align.center(
            Text(url),
            vertical="middle"
        ),
        box=box.ROUNDED
    )
    layout["Git.Url"].update(git_url)


def update_git_log(live: Live, path: WindowsPath):
    # cmd = r"D:\Git\bin\git.exe clone --progress git@github.com:By2048/_django_.git"
    layout["Git.Log"].update(Panel(Text("")))

    cmd = r"D:\Git\bin\git.exe pull"
    proc = subprocess.Popen(cmd, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    datas = []
    lines = []
    while line := proc.stdout.readline():
        datas.append(line)
        line = line.decode('gbk')

        if line == "Already up to date.\n":
            layout["Git.Log"].update(
                Panel(
                    Align.center(
                        Text(line.strip()),
                        vertical="middle"
                    )
                )
            )
            live.refresh()
            return

        if not line:
            continue

        if "\r" not in line:
            lines.append(line)
            data = "".join(lines)
            layout["Git.Log"].update(Panel(data))
            live.refresh()
            continue

        last_line = ""
        for _line_ in line.split("\r"):
            lines.append(_line_)
            last_line = _line_
            data = "".join(lines)
            layout["Git.Log"].update(Panel(data))
            live.refresh()
            lines.pop()

        lines.append(last_line)
        data = "".join(lines)
        layout["Git.Log"].update(Panel(data))
        live.refresh()


def init_gui():
    layout.name = "Content"
    layout["Content"].split_row(Layout(name="Folder", size=35), Layout(name="Git"))
    layout["Git"].split_column(Layout(name="Git.Url", size=3), Layout(name="Git.Log"))
    layout["Folder"].update(Panel(Text(""), box=box.ROUNDED))
    layout["Git.Url"].update(Panel(Text(""), box=box.ROUNDED))
    layout["Git.Log"].update(Panel(Text(""), box=box.ROUNDED))


def main():
    gui = Align.center(rich.panel.Panel(layout, width=w, height=h, box=rich.box.MINIMAL))
    init_gui()
    with Live(gui, auto_refresh=False, screen=False) as live:
        for folder_path in folder_paths:
            update_table_tree(folder_path)
            live.refresh()
            update_git_remote(folder_path)
            live.refresh()
            update_git_log(live, folder_path)


def test():
    gui = Align.center(rich.panel.Panel(layout, width=w, height=h, box=rich.box.MINIMAL))
    init_gui()
    update_table_tree(folder_paths[1])
    console.print(gui)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)