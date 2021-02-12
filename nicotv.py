import os
import html
import base64
from pprint import pprint
from collections import namedtuple
from typing import List, Union

import requests
from bs4 import BeautifulSoup
from rich.prompt import Prompt

base_url = "http://www.nicotv.club"


class Video(object):
    def __init__(self, title="", play_url="", download_url=""):
        self.title = title
        self.play_url = play_url
        self.download_url = download_url

    def __str__(self):
        return f"   Title:{self.title}\n" \
               f"    Play:{self.play_url}\n" \
               f"Download:{self.download_url}\n"


def get_all_link(detail_url) -> List:
    response = requests.get(detail_url)
    soup = BeautifulSoup(response.text, "html.parser")
    ul = soup.find("ul", class_="ff-playurl-tab-1")
    result = []
    for li in ul.find_all("li"):
        a = li.find("a")
        href = a["href"]
        href = href.strip("/")
        play_url = f"{base_url}/{href}"
        result.append(play_url)
    return result


def get_video(play_url) -> Video:
    video = Video(play_url=play_url)

    response = requests.get(play_url)
    soup = BeautifulSoup(response.text, "html.parser")
    ul = soup.find("ul", class_="ff-playurl")
    active_id = ul["data-active"]
    li = ul.find("li", attrs={"data-id": active_id})
    a = li.find("a")
    title = a.get_text()
    video.title = title

    player = soup.find("div", id="cms_player")
    script = player.find("script")
    download_url = script["src"]
    download_url = download_url.replace("/player.php?u=", "")
    download_url = download_url.split("&")[0]
    download_url = base64.b64decode(download_url).decode()
    download_url = download_url.split("?url=")[-1]
    download_url = download_url.rstrip("?")
    video.download_url = download_url

    return video


def download_video(video: Video):
    video_type = video.download_url.split(".")[-1]
    cmd = f"D:\\Aria2\\aria2c.exe " \
          f"{video.download_url} " \
          f"--out '{video.title}.{video_type}'"
    cmd = cmd.replace("'", '"')
    print(cmd)
    os.system(cmd)


def main():
    url = Prompt.ask("视频 [red][详情页\\播放页][/red] 地址")

    if "detail" in url:
        links = get_all_link(url)
        for link in links:
            video = get_video(link)
            download_video(video)

    if "play" in url:
        video = get_video(url)
        download_video(video)


def test():
    detail_url = "http://www.nicotv.me/video/detail/58086.html"
    play_url = "http://www.nicotv.me/video/play/58086-1-5.html"

    # links = get_all_link(detail_url)
    # for link in links:
    #     print(link)

    video = get_video(play_url)
    print(video)


if __name__ == '__main__':
    main()
    # test()
