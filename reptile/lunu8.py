import copy
import os
import time
import sys
import urllib.request
from pprint import pprint

import requests
from rich import print
from rich.prompt import Prompt
from bs4 import BeautifulSoup


# https://www.lunu8.com/

def download(url, name):
    cmd = f" D:\\Aria2\\aria2c.exe " \
          f" '{url}' " \
          f" --dir 'T:' " \
          f" --out '{name}' "
    cmd = cmd.replace("'", '"').strip()
    print(cmd)
    os.system(cmd)


def main():
    text = "[white on red]Arg1[/white on red]"
    text += "[red][图片第一页][/red]"

    url = Prompt.ask(text)

    session = requests.Session()

    response = session.get(f"{url}?page=1")
    soup = BeautifulSoup(response.text, "html.parser")

    # title = soup.find("h1", class_="title").get_text()
    total = soup.find("li", class_="next-page").previous_sibling.string

    for index in range(1, int(total) + 1):
        detail_url = f"{url}?page={index}"
        print(detail_url)
        if index == 1:
            soup = soup
        else:
            response = session.get(detail_url)
            soup = BeautifulSoup(response.text, "html.parser")
        try:
            image_url = soup.find("div", class_="entry")
            image_url = image_url.find("p").find("img").get("src")
            image_name = image_url.split('/')[-1]
            _name_, _type_ = image_name.split(".")
            image_name = f"{str(index).zfill(2)}.{_type_}"
        except:
            continue
        download(image_url, image_name)
        time.sleep(3)

    session.close()


if __name__ == '__main__':
    main()
