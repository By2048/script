#! /root/.pyenv/versions/_python_/bin/python/
import json
import os
import sys

import requests
from rich import box
from rich.live import Live
from rich.table import Table
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

path = 'D:\\Temp\\' if sys.platform == 'win32' else '/tmp/'
path = os.path.join(path, "bilibili.json")

chrome_driver_path = r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"


def backup():
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
    chrome_options = Options()
    chrome_options.add_argument(f'--window-size={w},{h}')
    chrome_options.add_argument(f'--window-position={x},{y}')

    chrome = webdriver.Chrome(executable_path=chrome_driver_path, chrome_options=chrome_options)

    url = 'https://api.bilibili.com/pgc/season/index/result' \
          '?season_version=-1' \
          '&area=-1' \
          '&is_finish=-1' \
          '&copyright=-1' \
          '&season_status=-1' \
          '&season_month=-1' \
          '&year=-1' \
          '&style_id=-1' \
          '&order=1' \
          '&st=1' \
          '&sort=0' \
          '&page={}' \
          '&season_type=1' \
          '&pagesize=5000' \
          '&type=1'

    url = url.format(1)
    chrome.get(url)
    chrome.minimize_window()

    data = chrome.find_element_by_tag_name("pre").text

    chrome.close()

    data = json.loads(data)

    data = data.get('data')

    table = Table(box=box.SIMPLE)
    table.add_column("Name", justify="right", width=40)
    table.add_column("Url", justify="left", width=60)

    old = {}  # 上一次获取的数据
    new = {}  # 本次获取的数据
    if os.path.exists(path):
        with open(path, encoding='utf-8') as file:
            old = json.load(file)

    with Live(table, refresh_per_second=4):
        for video in data.get('list'):
            badge = video.get('badge')
            if badge in ['限时免费']:
                _id_ = str(video['media_id'])
                _title_ = video['title']
                _link_ = video['link']
                new[_id_] = {'title': _title_, 'link': _link_}
                if _id_ in old:
                    table.add_row(video['title'], video['link'])
                else:
                    table.add_row(video['title'], f"[red]{video['link']}")

    with open(path, 'w+', encoding='utf-8') as file:
        json.dump(new, file)
