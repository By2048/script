#
import os
import threading
from pathlib import WindowsPath

folder = WindowsPath("E:\\GitX\\")

paths = []
for item in folder.iterdir():
    if not item.is_dir():
        continue
    paths.append(item)


def remote():
    for path in paths:
        cmd = rf'cd /d {path} & git remote -v'
        print(path)
        os.system(cmd)
        print()
        print()


def update(path):
    cmd = rf'cd /d {path} & git pull'
    print('\n')
    print(cmd)
    os.system(cmd)


def main():
    for path in paths:
        update(path)


def test():
    for path in paths:
        cmd = f'[red]cd[/red] /d {path} & git remote -v'
        print(cmd)


# t = threading.Thread(target=update, args=(path,))
# t.start()


if __name__ == '__main__':
    # remote()
    # test()
    main()
