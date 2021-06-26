from collections import namedtuple

# carbon
# gits
# .csv 文件将会被转换成 markdown 表格。
# .mermaid 将会被 mermaid 渲染。
# .dot 文件将会被 viz.js (graphviz) 渲染。
# .plantuml(.puml) 文件将会被 PlantUML 渲染。
# .pdf 文件将会被 pdf2svg 转换为 svg 然后被引用。

types_image = ['png', 'jpg', 'gif', 'jpeg', 'svg']

types_code = ['txt', 'py', 'md', 'json', 'html', 'css', 'less', 'js']

# key=width value=xxx
Command = namedtuple('Command', ['key', 'value'])

# index=1 name=file value=([\w\d\.]+)
Arg = namedtuple('Arg', ['index', 'name', 'value'])

# 编码转化
chars_encode = {chr(i): f'\\{chr(i)}' for i in b'()[]{}?*+-|^$\\.&~# \t\n\r\v\f'}
chars_decode = {v: k for k, v in chars_encode.items()}
