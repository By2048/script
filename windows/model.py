from typing import Dict, List
from pathlib import WindowsPath
from dataclasses import dataclass, field


@dataclass
class Desktop:
    name: str = ""
    info: str | list = ""
    icon: WindowsPath = None
    rename: Dict = None

    def __bool__(self):
        return bool(self.name) or bool(self.info) or bool(self.icon)

    def __init__(self, data=None):
        data = {} if data is None else data
        self.name = data.get("Name") or ""
        self.info = data.get("Info") or ""
        self.icon = data.get("Icon") or ""
        self.rename = data.get("Rename") or ""


@dataclass
class Lnk:
    name: str = ""
    target_path: WindowsPath = WindowsPath()
    working_directory: WindowsPath = WindowsPath()
    description: str = ""
    icon_location: WindowsPath = WindowsPath()

    def __bool__(self):
        return bool(self.name) or bool(self.target_path)

    def __init__(self, data: dict = None):
        data = {} if data is None else data
        self.name = data.get("Name") or ""
        self.target_path = data.get("TargetPath") or ""
        self.working_directory = data.get("WorkingDirectory") or ""
        self.description = data.get("Description") or ""
        self.icon_location = data.get("IconLocation") or ""


@dataclass
class Folder:
    path: WindowsPath = WindowsPath()
    # desktop: Desktop = Desktop()
    desktop: Desktop = field(default_factory=Desktop)
    lnks: List[Lnk] = None  # noqa

    def __repr__(self):
        data = f">folder  {self.path}"
        if self.desktop:
            data = data + "\n desktop "
            data = data + f"{self.desktop.name} {self.desktop.icon} {self.desktop.info}"
        if self.lnks:
            for lnk in self.lnks:
                data = data + "\n lnk     "
                data = data + f"{lnk.name} {lnk.target_path} {lnk.working_directory}"
        return data


@dataclass
class Script:
    type: str = "Bat"  # Bat Or PowerShell
    path: WindowsPath = None
    exe: WindowsPath = None
    args: list = None
    before: list = None
    after: list = None
    commands: list = None

    def __repr__(self):
        return self.exe

    def __bool__(self):
        return bool(self.exe)