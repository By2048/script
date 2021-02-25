#! /root/.pyenv/versions/_python_/bin/python/
import json
import os
import sys

import requests
from rich import box
from rich.live import Live
from rich.table import Table

path = 'D:\\Temp\\' if sys.platform == 'win32' else '/tmp/'
path = os.path.join(path, "bilibili.json")

chrome_driver_path = r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"

# order
# 0 更新时间
# 1 无
# 2 播放数量
# 3 追番人数
# 4 最高评分
# 5 开播时间
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
      '&pagesize=50' \
      '&type=1'


def main():
    old = {}  # 上一次获取的数据
    new = {}  # 本次获取的数据

    if os.path.exists(path):
        with open(path, encoding='utf-8') as file:
            if file.readlines():
                old = json.load(file)

    table = Table(box=box.SIMPLE)
    table.add_column("Name", justify="right", width=40)
    table.add_column("Url", justify="left", width=60)

    session = requests.Session()

    page = 1
    with Live(table, refresh_per_second=4):
        while True:
            response = session.get(url.format(page))
            response = response.json()
            data = response.get('data')
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
                        table.add_row(f"[red]{video['title']}", f"[red]{video['link']}")
            if not data.get('has_next') or page > 99:
                break
            page += 1

    session.close()

    with open(path, 'w+', encoding='utf-8') as file:
        json.dump(new, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
