#!/root/.pyenv/versions/_python_/bin/python

import shutil
import os
import sys
from enum import Enum

import fire


class Args(Enum):
    upgrade = '更新ZSH'
    update_themes = '更新主题'
    reset_themes = '还原主题'


def help():
    print('      upgrade | 更新ZSH')
    print('update_themes | 更新主题')
    print(' reset_themes | 还原主题')


files = [
    {
        'path': f"/root/.oh-my-zsh/themes/robbyrussell.zsh-theme",
        'replace': ('%c', '$PWD')
    }
]
backup = r'/root/backup/oh-my-zsh'

if not os.path.exists(backup):
    os.makedirs(backup)


def update_themes():
    for file in files:
        print(f"{file['path']}    {file['replace'][0]} -> {file['replace'][1]}")
        origin_file = file['path']
        backup_file = f"{backup}/{os.path.basename(origin_file)}"

        if not os.path.isfile(backup_file):
            shutil.copy(origin_file, backup_file)

        with open(backup_file, 'r', encoding='utf-8') as backup_data:
            _0, _1 = file['replace'][0], file['replace'][1]
            backup_data = backup_data.read().replace(_0, _1)

        with open(origin_file, 'w+', encoding='utf-8') as origin_data:
            for item in backup_data:
                origin_data.write(item)
    os.system('exec $SHELL')


def reset_themes():
    for item in os.listdir(backup):
        backup_path = os.path.join(backup, item)
        for file in files:
            if os.path.basename(file['path']) == item:
                print(f"{backup_path} -> {file['path']}")
                shutil.move(backup_path, file['path'])
                break
    os.system('exec $SHELL')


def upgrade():
    reset_themes()
    os.system('upgrade_oh_my_zsh')
    update_themes()


if __name__ == '__main__':
    fire.Fire()
