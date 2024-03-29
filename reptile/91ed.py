import sys
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
from rich.console import Console
from rich.prompt import Prompt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

try:
    from tool.system import get_browser_position
except ImportError:
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(path)
    from tool.system import get_browser_position

base_url = "https://www.91ed.com/"
chrome_driver_path = r"C:\Program Files\Google\Chrome\Application\chromedriver.exe"


class Video(object):
    def __init__(self, title="", play_url="", download_url=""):
        self.title = title
        self.play_url = play_url
        self.download_url = download_url

    def __str__(self):
        return f"   Title:{self.title}\n" \
               f"    Play:{self.play_url}\n" \
               f"Download:{self.download_url}\n"


def get_all_link(detail_url, select: list = None) -> List:
    response = requests.get(detail_url)
    soup = BeautifulSoup(response.text, "html.parser")
    div = soup.find("div", id='playlist2')
    ul = div.find("ul")
    result = []
    for li in ul.find_all("li"):
        a = li.find("a")
        href = a["href"]
        href = href.strip("/")
        play_url = f"{base_url}/{href}"
        result.append(play_url)
    if select:
        result = [result[item] for item in select]

    return result


def get_video(play_url) -> Video:
    video = Video(play_url=play_url)

    response = requests.get(play_url)
    soup = BeautifulSoup(response.text, "html.parser")

    video.title = soup.find('a', class_='btn btn-warm').get_text()

    win_x, win_y, win_w, win_h = get_browser_position(screen="screen_3_main")

    options = Options()
    options.add_argument(f'--window-size={win_w},{win_h}')
    options.add_argument(f'--window-position={win_x},{win_y}')

    browser = webdriver.Chrome(executable_path=chrome_driver_path, chrome_options=options)

    browser.get(play_url)
    browser.minimize_window()
    browser.implicitly_wait(10)

    browser.switch_to.frame(0)
    browser.switch_to.frame(0)

    element_video = browser.find_element_by_tag_name("video")
    download_url = element_video.get_attribute("src")
    browser.close()

    video.download_url = download_url

    return video


def download_video(video: Video):
    folder = os.getcwd()
    for file in os.listdir(folder):
        if video.title in file:
            return
    cmd = f" D:\\Aria2\\aria2c.exe " \
          f" '{video.download_url}' " \
          f" --out '{video.title}.mp4' "
    cmd = cmd.replace("'", '"').strip()
    print(f"\n\n[red]{copy.copy(cmd)}[/red]")
    os.system(cmd)


def main():
    text = "[white on red]Arg1[/white on red]"
    text += "[red][视频详情页\\视频播放页][/red]"
    text += " "
    text += "[white on red]Arg2[/white on red]"
    text += "[red][指定下载序号][/red]"

    url = Prompt.ask(text)

    if "detail" in url:
        select = None
        if " " in url:
            url, select = url.split()
            select = [int(item) for item in select.split(",")]
            select = [item - 1 if item > 0 else item for item in select]
        links = get_all_link(url, select)
        for link in links:
            video = get_video(link)
            download_video(video)

    if "play" in url:
        video = get_video(url)
        download_video(video)


def test():
    print()
    detail_url = "https://www.91ed.com/dm/zhanfushaonv.html"
    play_url = "https://www.91ed.com/vodplay/zhanfushaonv-2-2.html"

    # links = get_all_link(detail_url)
    # for link in links:
    #     print(link)

    video = get_video(play_url)
    print(video)

    # download_video(video)


if __name__ == '__main__':
    # main()
    test()
