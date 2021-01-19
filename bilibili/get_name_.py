import re
import json

import requests

# 番剧地址
url = "https://www.bilibili.com/bangumi/play/ss26281"


class Video(object):
    def __init__(self):
        self.index = 0
        self.name = ""

    def __str__(self):
        return f"{self.index} {self.name}"


class Collection(object):
    def __init__(self):
        self.title = ""
        self.video = []

    def append(self, item):
        self.video.append(item)

    def info(self):
        result = ""
        result += self.title
        result += "\n"
        if len(self.video) >= 10:
            for item in self.video:
                item.index = str(item.index).zfill(2)
        for item in self.video:
            result += f"{item.index} {item.name}\n"
        result.strip()
        return result


def main():
    response = requests.get(url)
    tags = re.search("(window.__INITIAL_STATE__=)(.*?)(;)", response.text)
    data = tags.groups()[1]
    data = json.loads(data)

    title = data['mediaInfo']['title']
    collection = Collection()
    collection.title = title
    for item in data['epList']:
        video = Video()
        video.index = item['title']
        video.name = item['longTitle']
        collection.append(video)
        
    print(collection.info())


if __name__ == '__main__':
    main()
