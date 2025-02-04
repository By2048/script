import os
import sys
import json
import shutil
from datetime import datetime

from pathlib import WindowsPath
from typing import List

from rich import print
from rich.prompt import Prompt

try:
    from rename.rename import change_name
except ImportError:
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(path)
    from rename.rename import change_name

path_ffmpeg = WindowsPath("D:\\FFmpeg\\ffmpeg.exe")
path_download = WindowsPath("V:\\#\\com.bilibili.app.in\\")
path_video = WindowsPath("T:\\#Video\\")

if os.environ.get("Debug"):
    path_download = WindowsPath("V:\\Video\\")
    path_video = WindowsPath("V:\\")

r"""
V:\Video\ (Path Download)
├─1010101 (Collection)
│  ├─c_101 (Video)
|  |  |-80
|  |  |  audio.m4s
│  |  |  index.json
│  |  |  video.m4s
|  |  |-64
|  |  |  audio.m4s
│  |  |  index.json
│  |  |  video.m4s
│  |  danmaku.xml
│  │  entry.json

80 64 指不同分辨率
一般来说只保留一个 越大越好
处理时如果存在多个 删除小的
"""


class Video(object):
    def __init__(self):
        self.owner = ""
        self.folder: WindowsPath = WindowsPath()
        self.index = ""
        self.part = ""
        self.title = ""
        self.entry: WindowsPath = WindowsPath()
        self.video: WindowsPath = WindowsPath()
        self.audio: WindowsPath = WindowsPath()

    def __bool__(self):
        return bool(self.entry) and bool(self.video) and bool(self.audio)

    def __str__(self):
        result = f"{'-> video_index'.rjust(20)} {self.index}\n"
        result += f"{' video_part'.rjust(28)} {self.part}\n"
        result += f"{'video_title'.rjust(28)} {self.title}"
        return result


class Collection(object):
    def __init__(self, folder):
        self.folder: WindowsPath = folder
        self.videos: [Video] = []

    @property
    def count(self):
        return len(os.listdir(self.folder))

    def __str__(self):
        result = f"  collection  {self.folder}"
        return result


def print_config():
    print()
    print(f'  [green]FFmpeg[/green]    {path_ffmpeg}')
    print(f'  [green]Download[/green]  {path_download}')
    print(f'  [green]Video[/green]     {path_video}')


def init_collections():
    collections = []

    for collection_folder in path_download.iterdir():
        collection_folder_path = path_download / collection_folder
        if not collection_folder_path.is_dir():
            continue
        collection = Collection(folder=collection_folder_path)
        videos = []
        for video_folder in collection_folder_path.iterdir():
            video = Video()
            video.folder = collection_folder_path / video_folder
            video.index = video_folder.name.replace("c_", "")
            videos.append(video)
        collection.videos = videos
        collections.append(collection)

    return collections


def init_collection_videos(collection: Collection):
    video: Video
    for video in collection.videos:

        # 删除较小分辨率的视频
        video_items: List[WindowsPath] = list(video.folder.iterdir())
        video_items = [item for item in video_items if item.is_dir()]
        if len(video_items) > 1:
            video_items = sorted(video_items, key=lambda x: int(x.name), reverse=True)
        video_item = video_items[0]

        video.entry = video.folder / 'entry.json'

        # 初始化视频文件
        video.folder = video_item
        video.video = video_item / 'video.m4s'
        video.audio = video_item / 'audio.m4s'

        with open(video.entry.as_posix(), 'r', encoding='utf-8') as file:
            data = json.load(file)
            owner = data.get('owner_name')
            part = data['page_data']['part']
            title = data['title']
            part = change_name(part)
            title = change_name(title)
            video.owner = owner
            video.part = part
            video.title = title


def join_video(video: Video):
    # 使用 ffmpeg 拼接视频

    if not video:
        print('')
        print('')
        print('-' * 66)
        print(f"下载文件缺失")
        print(f"  {video.title}")
        print(f"  {video.folder}")
        print('-' * 66)
        print('')
        print('')
        return

    name_config = (
        f"{video.owner} {video.title}",
        f"{video.title}",
        f"{video.part}" if video.title != video.part else "",
        f"{video.title} {video.part}" if video.title != video.part else "",
        f"{video.index} {video.title}",
        f"{video.index} {video.part} {video.title}" if video.part != video.title else "",
        f"{datetime.now().strftime('%Y-%m-%d')} {video.title}",
    )
    name_config = (item for item in name_config if item)
    names = {}
    for index, name in enumerate(name_config, 1):
        if name:
            names[f"{index}"] = name

    print()
    data = f"  # | [reverse]{video.folder}[/reverse] \n"
    for index, value in names.items():
        data += f"  [red]{index}[/red] | {value}\n"
    data = data.rstrip()

    print(data)

    check = Prompt.ask(f"  [red]#选择#[/red]", default="\\")

    check = "1" if check == "\\" else check
    if check == "\\\\":
        return

    if check not in names.keys():
        return

    name = names.get(check)
    if not name:
        return

    video_output = path_video / name

    cmd = f" {path_ffmpeg.as_posix()} " \
          f" -i {video.video} -i {video.audio} " \
          f" -c:v copy " \
          f" \"{video_output}.mp4\" "
    cmd = cmd.strip()
    print()
    print(cmd)
    print()
    os.system(cmd)
    # subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)


def clear_download():
    print()
    print(f"  [red]# {path_download}[/red]")
    check = Prompt.ask("  [red]# 删除下载文件夹 [/red]")
    if check == '\\':
        print("")
        try:
            shutil.rmtree(path_download)
        except Exception as e:
            pass
    print()
    print()


def test():
    pass


def setup():
    print_config()

    if not path_download.exists():
        print()
        print(f"  不存在路径 {path_download}")
        return

    collections = init_collections()
    for collection in collections:
        init_collection_videos(collection)
        for video in collection.videos:
            join_video(video)

    # clear_download()


if __name__ == '__main__':
    setup()