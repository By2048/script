import os

import sys
import win32api
import win32com
import win32com.client
from pathlib import WindowsPath

from loguru import logger


def get_exe_version(file: str | WindowsPath):
    file = WindowsPath(file) if isinstance(file, str) else file
    if not file.exists():
        return
    if not file.is_file():
        return
    file = file.as_posix()
    try:
        info = win32api.GetFileVersionInfo(file, os.sep)
        file_ms = info['FileVersionMS']
        file_ls = info['FileVersionLS']
        product_ms = info['ProductVersionMS']
        product_ls = info['ProductVersionLS']
        high = win32api.HIWORD
        low = win32api.LOWORD
        file_info = f"{high(file_ms)}.{low(file_ms)}.{high(file_ls)}.{low(file_ls)}"
        product_info = f"{high(product_ms)}.{low(product_ms)}.{high(product_ls)}.{low(product_ls)}"
        return file_info, product_info
    except Exception as e:
        return None, None


def get_exe_file_version(file: str | WindowsPath):
    return get_exe_version(file)[0]


def get_exe_product_version(file: str | WindowsPath):
    return get_exe_version(file)[1]


def lnk_to_exe(file: str):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(file)
    result = shortcut.Targetpath
    return result


if __name__ == '__main__':
    file = "D:\BitComet\BitComet.exe"
    result = get_exe_version(file)
    print(result)

    file = "D:\#Lnk\Dexpot.lnk"
    result = lnk_to_exe(file)
    print(result)