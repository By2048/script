import sys
import yaml
from typing import List
from pathlib import WindowsPath

from rich import get_console
from loguru import logger

logger.remove()
logger.add(sink=sys.stdout, colorize=True, level="DEBUG",
           format="<green>{file:<10}:{line}</green> | {message}")

from model import Folder, Script


def yaml_join(loader, node):
    nodes = loader.construct_sequence(node)
    return ' '.join([item for item in nodes])


yaml.add_constructor(r'!Join', yaml_join)

windows_config_folder = WindowsPath('E:\\Config\\Windows\\')
windows_config_files = []
for item in windows_config_folder.glob("**\\*.yaml"):
    if "~" in item.as_posix():
        continue
    if "Config.yaml" in item.as_posix():
        windows_config_files.insert(0, item)
    else:
        windows_config_files.append(item)

console = get_console()

windows_config: dict = {}

console.print()
for config_file in windows_config_files:
    logger.debug(f"Load {config_file}")
    with open(config_file, encoding="utf-8") as file:
        config_item: dict = yaml.unsafe_load(file)
        for key, value in config_item.items():
            if key not in windows_config.keys():
                windows_config[key] = value
            else:
                windows_config[key] |= value
console.print()

path_cache = WindowsPath(windows_config.get("#Cache"))
path_icon = WindowsPath(windows_config.get("#Icon"))
path_lnk = WindowsPath(windows_config.get("#Lnk"))
path_script = WindowsPath(windows_config.get("#Script"))
path_script_txt = WindowsPath(windows_config.get("#ScriptText"))
path_psl = WindowsPath(windows_config.get("#PowerShell"))

path_rename = windows_config.get("#PathRename")

# 文件夹配置
folders: List[Folder] = []
scripts: List[Script] = []

assert windows_config_folder
assert windows_config
assert path_icon
assert path_lnk