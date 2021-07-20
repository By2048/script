import json
from collections import namedtuple

# carbon
# gits
# .csv 文件将会被转换成 markdown 表格。
# .mermaid 将会被 mermaid 渲染。
# .dot 文件将会被 viz.js (graphviz) 渲染。
# .plantuml(.puml) 文件将会被 PlantUML 渲染。
# .pdf 文件将会被 pdf2svg 转换为 svg 然后被引用。

# 所有的转换规则
patterns = []

types_image = ['png', 'jpg', 'gif', 'jpeg', 'svg']
types_code = ['txt', 'py', 'md', 'json', 'html', 'css', 'less', 'js']

re_image_str = '|'.join(types_image)
re_image_len = ' ' * len(re_image_str)

# test
re_code_str = '|'.join(types_code)
re_code_len = ' ' * len(re_code_str)

# key=width value=xxx
Command = namedtuple('Command', ['key', 'value'])

# index=1 name=file value=([\w\d\.]+)
Arg = namedtuple('Arg', ['index', 'name', 'value'])
# test

# 编码转化
chars_encode = {chr(i): f'\\{chr(i)}' for i in b'()[]{}?*+-|^$\\.&~# \t\n\r\v\f'}
chars_decode = {v: k for k, v in chars_encode.items()}

carbon_args: dict = {}

# *\carbon\lib\routing.js
routing = [
    'bg:backgroundColor',
    't:theme',
    'wt:windowTheme',
    'l:language',
    'ds:dropShadow',
    'dsyoff:dropShadowOffsetY',
    'dsblur:dropShadowBlurRadius',
    'wc:windowControls',
    'wa:widthAdjustment',
    'pv:paddingVertical',
    'ph:paddingHorizontal',
    'ln:lineNumbers',
    'fl:firstLineNumber',
    'fm:fontFamily',
    'fs:fontSize',
    'lh:lineHeight',
    'si:squaredImage',
    'es:exportSize',
    'wm:watermark',
    'sl:selectedLines',
]

for item in routing:
    item = item.split(':')
    carbon_args[item[0]] = item[1]
    carbon_args[item[1]] = item[0]

with open('carbon-config.json', 'r', encoding='utf-8') as file:
    _carbon_ = file.readlines()
    _carbon_ = ''.join(_carbon_)
    carbon: dict = json.loads(_carbon_)
    del file, _carbon_
