import inspect
import os
import re
from pathlib import Path

from config import *


# 文件夹遍历 Dos Tree 效果
def tree(path, level=1):
    # 实现类 Dos Tree 效果
    if level == 1:
        print(path)
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        print('│  ' * (level - 1) + '│--' + item)
        if os.path.isdir(full_path):
            tree(full_path, level + 1)


def remove_empty_markdown(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith('.md') and os.path.getsize(os.path.join(root, file)) == 0:
                path = os.path.join(root, file)
                print(path.ljust(30) + str(os.path.getsize(os.path.join(root, file))))
                os.remove(path)


def str_to_bool(value):
    data = {
        'true': True,
        'True': True,
        'false': False,
        'False': False,
    }

    if value in data.keys():
        return data[value]

    return value


def try_str_to_num(value):
    if isinstance(value, str):
        if value.lstrip('-').isdigit():
            value = int(value)
            return value
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            return value
    return value


def change(arg: str):
    # 命令
    result = {}

    if not arg:
        return result

    # {start:1 end:3}
    # k:v命令
    if '{' in arg and '}' in arg:
        arg = arg.lstrip("{").rstrip("}").strip()
        arg = arg.split(" ")
        for o in arg:
            k, v = o.split(':', 1)
            v = str_to_bool(v)
            v = try_str_to_num(v) if not isinstance(v, bool) else v
            result[k] = v
        return result

    # 快速命令
    if ':' in arg:

        # label:test
        if re.match(r'label:\w+', arg):
            arg = arg.split(":")
            result['function'] = arg[-1]
            return result

        return result


def get_file_path(file):
    work_folder = os.environ.get('work_folder')
    if work_folder:
        path = work_folder
    else:
        path = os.path.dirname(__file__)
    path = os.path.join(path, file)
    path = Path(path).as_posix()
    return path


def file_encode(data: str):
    for k, v in chars_encode.items():
        data = data.replace(k, v)
    return data


def file_decode(data: str):
    for k, v in chars_decode.items():
        data = data.replace(k, v)
    return data


def get_new_file_path(file_path):
    # file_type md.md
    file_name, file_type = os.path.splitext(file_path)
    file_folder = os.path.dirname(os.path.abspath(file_path))
    new_file_path = os.path.join(file_folder, f'{file_name}.preview{file_type}')
    return new_file_path


def open_file(file_full_path: str, command: dict = None):
    # 打开文件 优先预览文件
    file_preview = get_new_file_path(file_full_path)
    if os.path.isfile(file_preview):
        file_full_path = file_preview

    with open(file_full_path, 'r', encoding='utf-8') as file:
        data = file.readlines()

    command = command or {}

    if 'label' in command:
        label_name = command['label']
        rule = rf"""(?<=\n)(?:{label_name})([\s\S]+?)(?:{label_name})(?=\n)"""

        data = ''.join(data)
        data = '\n\n' + data + '\n\n'

        result = re.findall(rule, data)
        data = result[0] if len(result) == 1 else ""

    if 'function' in command:
        function_name = command['function']
        rule = rf"""(?<=\n\n)(def )({function_name})(\()([\s\S]+?)(:)([\S\s]+?)(?=\n\n)"""

        data = ''.join(data)
        data = '\n\n' + data + '\n\n'

        result = re.findall(rule, data)
        data = result[0] if len(result) == 1 else ""

    if 'start' in command and 'end' in command:
        start = command['start'] - 1
        end = command['end']
        data = data[start:end]

    data = ''.join(data)
    data = data.strip("\n")
    # data = file_encode(data)

    return data


if __name__ == '__main__':
    note_path = "T:\\"

    tree(note_path)

# def get_all_md_path(rootPath):
#     all_path = []
#     for root, dirs, files in os.walk(rootPath):
#         for file in files:
#             if file.endswith('.md'):
#                 file_path = os.path.join(root, file)
#                 file_path = file_path.replace(start_path, '')
#                 all_path.append(file_path[1:])
#     return all_path
#
#
# # 获取所有的笔记路径
# def get_all_note_path():
#     # 所有的笔记本文件路径
#     note_paths = []
#     paths = os.listdir(note_book_path)
#     for path in paths:
#         # 去除主目录上以 排除的文件夹 README.md 文件
#         if path in ignore_folder or path in ignore_file:
#             continue
#         note_path = os.path.join(note_book_path, path)
#         note_paths.append(note_path)
#     return note_paths
#
#
# # 判断路径中是否包含被忽略的文件夹
# def is_exit_ignore_folder(base_path):
#     split_paths = base_path.split('\\')
#     for _path in split_paths:
#         if _path in ignore_folder:
#             return True
#     return False
#
#
# # 判断是否是由Yu_Writer软件创建的文件夹
# def is_Yu_Writer_folder(path):
#     split_paths = path.split('.')
#     if len(split_paths) == 1:
#         return False
#     if split_paths[1] == 'resource':
#         return True
#     else:
#         return False
#
#
# if __name__ == '__main__':
#     all_path = get_all_note_path()
#     print('\n'.join(all_path))
#     pass
