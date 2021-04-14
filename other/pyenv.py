import os
import sys
import time

import fire

folder = "D:\\Python\\"


def show():
    data = os.listdir(folder)
    data = [item for item in data if not (item.startswith("_") and item.endswith("_"))]
    print(data)


"""

D:\python\3.8.9\python.exe -m pip install --upgrade pip


D:\Python\3.8.9\Scripts\pip.exe install virtualenv


D:\Python\3.8.9\Scripts\virtualenv.exe D:\Python\_3.8.9_\ --python=D:\python\3.8.9\python.exe


D:\Python\_3.8.9_\Scripts\activate.bat




"""


def create(source, name):
    command = fr"""
    {folder}\{source}\python.exe -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
    {folder}\{source}\Scripts\pip.exe install virtualenv -i https://pypi.tuna.tsinghua.edu.cn/simple
    {folder}\{source}\Scripts\virtualenv.exe {folder}\{name}\ --python={folder}\{source}\python.exe
    
    """
    command = command.replace("\\\\", "\\")
    command = command.strip()

    for cmd in command.split("\n"):
        cmd = cmd.strip()
        print(cmd)
        os.system(cmd)
        time.sleep(3)


def activate(name):
    command = fr"{folder}\{name}\Scripts\activate.bat"
    command = command.replace("\\\\", "\\")
    command = command.strip()
    os.system(command)


def delete(env_name):
    pass


if __name__ == '__main__':
    pass
    # fire.Fire()
    # list()
    # pass
    # show()
    # create("3.7.8", "_python_")
    # create("3.9.4", "_3.9.4_")
