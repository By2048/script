import os
import sys
import time
from pathlib import WindowsPath

sys.path.insert(0, WindowsPath(__file__).parents[1].as_posix())

from model import Desktop, Lnk, Script, Folder
from desktop import init_desktop
from folder import init_folders
from config import console, folders, scripts
from desktop import init_desktop, create_desktop, flush_desktop
from lnk import init_lnk, create_lnk
from script import init_scripts, create_script, create_script_txt


def help():
    text = ""
    text += "\n[red]All     [/red] : [green]帮助信息 默认[/green]"
    text += "\n[red]Help    [/red] : [green]帮助信息[/green]"
    text += "\n[red]Desktop [/red] : [green]文件信息[/green]"
    text += "\n[red]Lnk     [/red] : [green]文件链接[/green]"
    text += "\n[red]Script  [/red] : [green]脚本文件[/green]"
    text += "\n"
    console.print(text)


def main():
    #
    # help \ desktop \ lnk \ script \ all
    args = sys.argv[1:] if len(sys.argv) > 1 else ["all"]

    fun = arg = ""
    if len(args) == 0:
        fun = "all"
    elif len(args) == 1:
        fun = args[0]
    elif len(args) == 2:
        fun = args[0]
        arg = args[1]

    if fun == "help":
        help()
        return

    init_folders(filter=arg)

    if fun.lower() in ["folder", "desktop", "all"]:
        console.clear()
        console.print()
        init_desktop()
        create_desktop()
        flush_desktop()
        time.sleep(3)

        console.clear()
        console.print()
        init_lnk()
        create_lnk()
        time.sleep(3)
        console.clear()

    if fun.lower() in ["script", "all"]:
        console.print()
        console.print()
        init_scripts()
        create_script()

        console.print()
        create_script_txt()
        time.sleep(3)
        console.clear()


if __name__ == '__main__':
    main()