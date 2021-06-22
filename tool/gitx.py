import os
import threading

folder = "E:\\GitX\\"

paths = [os.path.join(folder, item) for item in os.listdir(folder)]


def remote():
    for path in paths:
        cmd = rf'cd /d {path} & git remote -v'
        print(path)
        os.system(cmd)
        print()
        print()


def update(path):
    cmd = rf'cd /d {path} & git pull'
    print(cmd)
    os.system(cmd)


def main():
    for item in paths:
        t = threading.Thread(target=update, args=(item,))
        t.start()


if __name__ == '__main__':
    main()
    # remote()
