import os
import re
import copy
import json
import shutil
from pprint import pprint
from pathlib import WindowsPath

# https://code.visualstudio.com/docs/getstarted/keybindings

path_source = WindowsPath(r"D:\VSCodeUser\User\KeyBindings.json")
path_backup = WindowsPath(r"D:\VSCodeUser\User\KeyBindings.Backup.json")
path_format = WindowsPath(r"D:\VSCodeUser\User\KeyBindings.Format.json")

shutil.copy(path_source, path_backup)

print()
print(f"   {path_source} \n"
      f"-> {path_backup}")
print()

print(f"path_source {path_source}")
print(f"path_backup {path_backup}")
print(f"path_format {path_format}")
print()


def json_format(data: dict):
    key = data.get("key", "")
    command = data.get("command", "")
    when = data.get("when", "")

    key = key.replace("\\", "\\\\")
    command = command.replace("\\", "\\\\")
    when = when.replace("\\", "\\\\")

    result = ""
    result += f'{{ "key" : "{key}" {" " * (30 - len(key))}  ,  '
    result += f'"command" : "{command}" {" " * (60 - len(command))}'
    if not when:
        result += " }  ,"
    else:
        result += f'    ,  "when" : "{when}" }}, '

    return result


def format_config():
    with open(path_backup, 'r', encoding='utf-8') as file:
        data = file.readlines()

    data = "".join([item.lstrip() for item in data])

    re_key = '"[\\\d\w\+\s_]+"'
    re_command = '"[\\\d\w\-\+\.,]+"'
    re_when = '"[\s\S]+?"'

    _match = rf'''
    1      2        3 key        4    5         6 command
    (\{{\n)("key": )({re_key})(,\n)("command": )({re_command})(,?)(\n\}})(,?)
    '''.strip().split("\n")[-1].strip()
    print(_match)
    _get = r'{ "key" : \3 , "command" : \6 } ,'
    data = re.sub(_match, _get, data)

    _match = rf'''
    1     2        3 key        4    5          6 command    7    8         9 when
    (\{{\n)("key": )({re_key})(,\n)("command": )({re_command})(,\n)("when": )({re_when})(\n\}})(,?)
    '''.strip().split("\n")[-1].strip()
    print(_match)
    _get = r'{ "key" : \3 , "command" : \6 , "when" : \9 } ,'
    data = re.sub(_match, _get, data)

    _match = rf'''
    1     2      3      4        5 key     6    7      8            9 command
    (//\s)(\{{\n)(//\s+)("key": )({re_key})(,\n)(//\s+)("command": )({re_command})(,?)(\n)(//\s+\}})(,?)
    '''.strip().split("\n")[-1].strip()
    print(_match)
    _get = r'// { "key" : \5 , "command" : \9 } ,'
    data = re.sub(_match, _get, data)

    _match = rf'''
    1     2      3      4        5 key     6    7      8            9 command     10   11     12        13 when
    (//\s)(\{{\n)(//\s+)("key": )({re_key})(,\n)(//\s+)("command": )({re_command})(,\n)(//\s+)("when": )({re_when})(\n//\s\}})(,?)
    '''.strip().split("\n")[-1].strip()
    print(_match)
    _get = r'// { "key" : \5 , "command" : \9 , "when" : \13 } ,'
    data = re.sub(_match, _get, data)

    with open(path_format, "w", encoding='utf-8') as file:
        file.write(data)


def test():
    with open(path_format, 'r', encoding='utf-8') as file:
        data = file.readlines()
    data = [item.strip() for item in data]

    content = ""
    for index, item in enumerate(data):
        if item.startswith("//"):
            # if item == "// ":
            #     content += "\n"
            # else:
            #     content += item
            content += item + "\n"
            continue
        if item.endswith(","):
            item = item.rstrip(",")
        try:
            item = json.loads(item)
            item = json_format(item)
            content += item
        except json.decoder.JSONDecodeError:
            content += item
        content += "\n"

    path_test = WindowsPath(r"T:\KeyBindings.Test.json")
    with open(path_test, "w", encoding='utf-8') as file:
        file.write(content)


if __name__ == '__main__':
    format_config()
    # test()