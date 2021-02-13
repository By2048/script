import os
import html
import time
import copy
import base64
from pprint import pprint
from collections import namedtuple
from typing import List, Union

import requests
from bs4 import BeautifulSoup
from rich import print
from rich.prompt import Prompt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

base_url = "http://www.nicotv.club"
chrome_driver_path = r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"

screen_x, screen_y = 0, 0
screen_xx, screen_yy = 3840, 2160
screen_w = screen_xx - screen_x
screen_h = screen_yy - screen_y
screen_dpi = 2

w = screen_w * (5 / 6)
h = screen_h * (8 / 9)
x = screen_x + (screen_w - w) / 2
y = screen_y + (screen_h - h) / 2

x, y = x / screen_dpi, y / screen_dpi
w, h = w / screen_dpi, h / screen_dpi
x, y, w, h = int(x), int(y), int(w), int(h)


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
    div = soup.find("div", class_="ff-playurl-tab")
    ul = div.find("ul", class_="active")
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

    if ".mp4" not in download_url:
        chrome_options = Options()
        chrome_options.add_argument(f'--window-size={w},{h}')
        chrome_options.add_argument(f'--window-position={x},{y}')

        chrome = webdriver.Chrome(executable_path=chrome_driver_path, chrome_options=chrome_options)

        chrome.get(play_url)
        chrome.implicitly_wait(10)

        chrome.switch_to.frame(0)
        chrome.switch_to.frame(0)

        element_video = chrome.find_element_by_tag_name("video")
        download_url = element_video.get_attribute("src")
        chrome.close()

    video.download_url = download_url
    return video


def download_video(video: Video):
    cmd = f" D:\\Aria2\\aria2c.exe " \
          f" '{video.download_url}' " \
          f" --out '{video.title}.mp4' "
    cmd = cmd.replace("'", '"').strip()
    print(f"[red]{copy.copy(cmd)}[/red]")
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
    # chrome
    detail_url = "http://www.nicotv.me/video/detail/56828.html"
    play_url = "http://www.nicotv.me/video/play/56828-1-1.html"

    # requests
    # detail_url = "http://www.nicotv.me/video/detail/58100.html"
    # play_url = "http://www.nicotv.club/video/play/58100-1-1.html"

    # links = get_all_link(detail_url)
    # for link in links:
    #     print(link)
    #
    # video = get_video(play_url)
    # print(video)
    # download_video(video)


if __name__ == '__main__':
    main()
    # test()
