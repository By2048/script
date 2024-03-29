import hashlib
import os

from rename import Rename

folder = "T:\\收藏\\"


def rule(item):
    # 已经重命名为文件的MD5  xx_md5_xxx.jpg 长度(36)
    if len(item) == 36:
        return

    item_type = item.split('.')[-1]
    item_full_path = os.path.join(folder, item)
    hash_md5 = hashlib.md5()
    with open(item_full_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    item_md5 = hash_md5.hexdigest()
    return f"{item_md5}.{item_type}"


if __name__ == '__main__':
    rename = Rename()
    rename.folder = folder
    rename.rule = rule
    rename.init()
    rename.command()
    rename.print()
    rename.start()