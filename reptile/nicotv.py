import json
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

base_url = "http://www.nicotv.club"
chrome_driver_path = r"C:\Program Files\Google\Chrome\Application\chromedriver.exe"

download_folder = os.getcwd()
config_file = os.path.join(os.getcwd(), 'config.json')


# download_folder = "T:\Anime\平稳世代的韦驮天们"
# config_file = "T:\Anime\平稳世代的韦驮天们\config.json"


class Video(object):
    def __init__(self, title="", play_url="", download_url=""):
        self.title = title
        self.play_url = play_url
        self.download_url = download_url

    def __str__(self):
        return f"   Title:{self.title}\n" \
               f"    Play:{self.play_url}\n" \
               f"Download:{self.download_url}\n"


def get_all_link(detail_url, select: list = None, ignore: list = None) -> List:
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

    if select:
        result = [result[item] for item in select]

    if ignore:
        obj = []
        for index, item in enumerate(result):
            if index not in ignore:
                obj.append(item)
        result = obj

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
    for file in os.listdir(download_folder):
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

    url = None
    select = []
    ignore = []

    if os.path.isfile(config_file):
        with open(config_file, 'r', encoding='utf-8') as file:
            file = json.loads(file.read())
            url = file.get('url')

        index = 0
        for file in os.listdir(download_folder):
            if file.endswith(('.mp4',)):
                ignore.append(index)
                index += 1
        ignore.reverse()

    if not url:
        arg = Prompt.ask(text)
        if " " in arg:
            url, select = url.split()
            select = [int(item) for item in select.split(",")]
            select = [item - 1 if item > 0 else item for item in select]
        else:
            url = arg

    if "detail" in url:
        if not os.path.isfile(config_file):
            with open(config_file, 'w+', encoding='utf-8') as file:
                data = {"url": url}
                json.dump(data, file)

        links = get_all_link(url, select, ignore)

        print()
        print(f"[red]url[/red]  : {url}")
        if not links:
            print(f"[red]link[/red] : None")
        for link in links:
            print(f"[red]link[/red] : {link}")
        print()

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
