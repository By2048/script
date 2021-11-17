import os

import sys
import win32api
import win32com
import win32com.client

from loguru import logger


def version(file: str):
    try:
        info = win32api.GetFileVersionInfo(file, os.sep)
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        high = win32api.HIWORD
        low = win32api.LOWORD
        result = f"{high(ms)}.{low(ms)}.{high(ls)}.{low(ls)}"
        return result
    except Exception as e:
        logger.exception(e)
        return None


def lnk_to_exe(file: str):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(file)
    result = shortcut.Targetpath
    return result


if __name__ == '__main__':
    file = "D:\BitComet\BitComet.exe"
    result = version(file)
    print(result)

    file = "D:\#Lnk\Dexpot.lnk"
    result = lnk_to_exe(file)
    print(result)
