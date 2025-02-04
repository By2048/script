import re
import os
import sys
import json
import time
import math
import subprocess

from pathlib import WindowsPath

from rich import box, print
from rich.text import Text
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.live import Live

console = Console()

# padding 1  border 1
# folder 1  space 1  tree 20  space 1  page 1
# border 1  padding 1

page_size = 30

gui_h = 8 + page_size
gui_w = 140

gui_x = int((console.width - gui_w) / 2)
gui_y = int((console.height - gui_h) / 2)

total_left = 35
tree_width = total_left - 7

folder = WindowsPath(r"E:\\Git\\")
if len(sys.argv) > 1:
    folder = sys.argv[1]
    folder = WindowsPath(folder)

if not folder:
    print()
    print(f"[red]Git Folder Not Exist[/red]")
    print()
    sys.exit()

folder_paths = list(folder.iterdir())
folder_paths = [item for item in folder_paths if item.is_dir()]
folder_paths = [item for item in folder_paths if not item.name.startswith("#")]
folder_names = [item.name for item in folder_paths]

folder_pages = []
for i in range(0, len(folder_paths), page_size):
    folder_pages.append(folder_paths[i:i + page_size])
page_total = len(folder_pages)

layout = Layout(name="Content")


def git_clone():
    # cmd = r"D:\Git\bin\git.exe clone --progress https://github.com/fatedier/frp.git"
    pass


def update_table_tree(path: WindowsPath):
    table = Table(box=None, padding=0, show_footer=False, show_header=False,
                  title=f"{folder}\\", title_style="white",
                  caption=f"1 / {page_size}", caption_style="white")
    table.add_column(justify="left", width=2)
    table.add_column(width=1)
    table.add_column(justify="left", width=tree_width)

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
        index = str(index).zfill(2)
        if path == value:
            table.add_row(index, "", value.name, style="Black On White")
        else:
            table.add_row(index, "", value.name)

    # 第一行是空行
    if offset := page_size - (len(table.rows) - 1):
        for _ in range(0, offset):
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
    content = Panel(Align.center(Text("Start Update ..."), vertical="middle"))
    layout["Git.Log"].update(content)
    live.refresh()

    cmd = r"D:\Git\bin\git.exe pull"
    proc = subprocess.Popen(cmd, cwd=path,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

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
            time.sleep(1)
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
    time.sleep(3)


def init_gui():
    layout["Content"].split_row(
        Layout(name="Folder", size=total_left),
        Layout(name="Git")
    )
    layout["Git"].split_column(
        Layout(name="Git.Url", size=3),
        Layout(name="Git.Log")
    )
    layout["Folder"].update(Panel(Text(""), box=box.ROUNDED))
    layout["Git.Url"].update(Panel(Text(""), box=box.ROUNDED))
    layout["Git.Log"].update(Panel(Text(""), box=box.ROUNDED))


def main():
    gui = Align.center(Panel(layout, width=gui_w, height=gui_h, box=box.MINIMAL))
    init_gui()
    with Live(gui, auto_refresh=False, screen=False) as live:
        for folder_path in folder_paths:
            update_table_tree(folder_path)
            live.refresh()
            update_git_remote(folder_path)
            live.refresh()
            update_git_log(live, folder_path)
            live.refresh()


def test():
    gui = Align.center(Panel(layout, width=gui_w, height=gui_h, box=box.MINIMAL))
    init_gui()


if __name__ == '__main__':
    # test()
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()