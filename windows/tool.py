import os
import ctypes
import win32api
import subprocess
from pathlib import WindowsPath
from win32comext.shell import shell, shellcon

from rich.panel import Panel
from rich.text import Text
from rich.align import Align

from config import path_psl, console


def flush():
    # 刷新文件夹图片
    ctypes.windll.shell32.SHChangeNotify(
        shellcon.SHCNE_ASSOCCHANGED,
        shellcon.SHCNF_IDLIST,
        0,
        0
    )


def center_panel_text(text, title="", width=99):
    text = Text(text)
    panel = Panel(text, title=title, title_align="center",
                  width=width, border_style="red")
    panel = Align.center(panel)
    console.print(panel)
    console.print()