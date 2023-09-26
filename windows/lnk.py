import os
import time

from rich.align import Align
from rich.panel import Panel

from model import Lnk, Folder
from config import folders, scripts, console
from config import path_tmp, path_lnk, path_icon


def create_lnk_file(lnk: Lnk):
    if not lnk:
        return

    tmp_vbs_path = path_tmp / "lnk.vbs"

    content = f'Set ws = WScript.CreateObject("WScript.Shell") \n' \
              f'Set lnk = ws.CreateShortcut("{path_lnk / lnk.name}") \n' \
              f'lnk.TargetPath = "{lnk.target_path}" \n' \
              f'lnk.WorkingDirectory = "{lnk.working_directory}\\" \n' \
              f'lnk.Description = "{lnk.description}" \n' \
              f'lnk.IconLocation = "{lnk.icon_location}" \n' \
              f'lnk.Save()'

    with open(tmp_vbs_path, "w", encoding="gbk") as file:
        file.write(content)

    os.system(f"start {tmp_vbs_path}")
    time.sleep(0.1)


def init_lnk():
    folder: Folder
    for folder in folders:
        lnk_default_exe = folder.path / f"{folder.path.name}.exe"
        if not folder.lnks and lnk_default_exe.exists():
            lnk = Lnk()
            lnk.name = f"{folder.path.name}.lnk"
            lnk.target_path = folder.path / f"{folder.path.name}.exe"
            lnk.working_directory = folder.path
            lnk.description = folder.path.name
            lnk.icon_location = folder.desktop.icon
            folder.lnks = [lnk]
            continue

        for lnk in folder.lnks:
            if not lnk and not lnk_default_exe.exists():
                continue

            lnk.name = lnk.name or f"{folder.path.name}.lnk"
            if not lnk.name.endswith(".lnk"):
                lnk.name = f"{lnk.name}.lnk"
            if lnk.target_path:
                lnk.target_path = folder.path / lnk.target_path
            else:
                lnk.target_path = folder.path / f"{folder.path.name}.exe"
            if lnk.working_directory:
                lnk.working_directory = folder.path / lnk.working_directory
            else:
                lnk.working_directory = folder.path

            lnk.description = lnk.description or folder.desktop.name or folder.path.name

            if lnk.icon_location:
                if str(lnk.icon_location).endswith(".ico"):
                    lnk.icon_location = path_icon / lnk.icon_location
                elif str(lnk.icon_location).endswith(".exe"):
                    lnk.icon_location = folder.path / lnk.icon_location
                else:
                    lnk.icon_location = folder.desktop.icon
            else:
                lnk.icon_location = folder.desktop.icon


def create_lnk():
    lnks_name = []

    for folder in folders:
        if not folder.lnks:
            continue
        for lnk in folder.lnks:
            if not lnk:
                continue
            create_lnk_file(lnk)
            lnks_name.append(lnk.name.rstrip(".lnk"))

    lnks_name.sort()
    text = ""
    for index, item in enumerate(lnks_name, start=1):
        text += f"{item:<20}"
        if index % 5 == 0:
            text += "\n"

    panel = Panel(text, title=f"{path_lnk}\\", title_align="center",
                  width=120, border_style="red")
    console.print()
    console.print()
    console.print(Align.center(panel))