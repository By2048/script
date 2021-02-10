import os
import html
import base64
from pprint import pprint
from collections import namedtuple
from typing import List

import requests
from bs4 import BeautifulSoup
from rich.prompt import Prompt

base_url = "http://www.nicotv.club"
Video = namedtuple("Video", "title play_url download_url")


def get_video_download_url(play_url):
    response = requests.get(play_url)
    soup = BeautifulSoup(response.text, "html.parser")
    player = soup.find("div", id="cms_player")
    script = player.find("script")
    download_url = script["src"]
    download_url = download_url.replace("/player.php?u=", "")
    download_url = download_url.split("&")[0]
    download_url = base64.b64decode(download_url).decode()
    download_url = download_url.split("?url=")[-1]
    download_url = download_url.rstrip("?")
    return download_url


def get_all_video(detail_url) -> List["Video"]:
    response = requests.get(detail_url)
    soup = BeautifulSoup(response.text, "html.parser")
    ul = soup.find("ul", class_="ff-playurl-tab-1")
    result = []
    for li in ul.find_all("li"):
        a = li.find("a")
        href = a["href"]
        title = a.get_text()
        play_url = f"{base_url}/{href}"
        download_url = get_video_download_url(play_url)
        result.append(Video(title=title, play_url=play_url, download_url=download_url))

    return result


def download_video(video: Video, folder):
    folder = folder.rstrip("\\")
    video_type = video.download_url.split(".")[-1]
    cmd = f"D:\\Aria2\\aria2c.exe " \
          f"{video.download_url} " \
          f"--dir '{folder}' " \
          f"--out '{video.title}.{video_type}'"
    cmd = cmd.replace("'", '"')
    print(cmd)
    os.system(cmd)


def main():
    folder = Prompt.ask("保存的文件夹名字")
    detail_url = Prompt.ask("视频详情页地址")

    folder = f"T:\\{folder}"

    if not os.path.exists(folder):
        os.makedirs(folder)

    videos = get_all_video(detail_url)
    for video in videos:
        download_video(video, folder)


def test():
    folder = "七大罪 第四季 愤怒的审判"
    detail_url = "http://www.nicotv.me/video/detail/58086.html"
    folder = f"T:\\{folder}\\"

    videos = get_all_video(detail_url)
    for video in videos:
        download_video(video, folder)


if __name__ == '__main__':
    main()
    # test()
