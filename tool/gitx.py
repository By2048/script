import os
import threading


def update(path):
    cmd = rf'cd /d {path} & git pull'
    print(cmd)
    os.system(cmd)


def main():
    path = "E:\\GitX\\"
    paths = [os.path.join(path, item) for item in os.listdir(path)]
    for item in paths:
        t = threading.Thread(target=update, args=(item,))
        t.start()


if __name__ == '__main__':
    main()
