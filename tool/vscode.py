import os
import re
import copy
import json
from pprint import pprint

path = r"D:\VSCodeData\User\keybindings.json"
path_format = r"E:\Project\Demo\json.json"


def json_print(data: dict):
    key = data.get("key")
    command = data.get("command")
    when = data.get("when")

    key = key.replace("\\", "\\\\")
    command = command.replace("\\", "\\\\")
    when = when.replace("\\", "\\\\") if when else ...

    result = f"""{{  "key"     : "{key}" ,\n   "command" : "{command}" """
    if when:
        result += ",\n"
        result += f"""   "when"    : "{when}"  }}, """
    else:
        result += " },"
    return result


def main():
    data = ""

    with open(path, 'r', encoding='utf-8') as file:
        config = file.readlines()

    for item in config:
        if not item:
            continue
        item = item.lstrip()
        data += item

    data = re.sub(r"{\n", "{", data)
    data = re.sub(r",\n", ",", data)
    data = re.sub(r"\n},", "},\n", data)
    data = re.sub(r"\n}", "},\n", data)

    data = data.split("\n")

    content = ""
    for index, item in enumerate(data):
        if item.startswith("//"):
            content += item
            content += "\n"
            continue
        if item.endswith(","):
            item = item.rstrip(",")
        try:
            item = json.loads(item)
            item = json_print(item)
            content += item
        except json.decoder.JSONDecodeError:
            content += item
        content += "\n"

    with open(path_format, "w") as file:
        file.write(content)


def test():
    pass


if __name__ == '__main__':
    print("\n" * 3)
    main()
    print("\n" * 3)
    # test()
