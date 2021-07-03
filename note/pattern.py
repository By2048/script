import os
import re
import copy
import string
import math
import subprocess
import inspect
from urllib.parse import quote

from config import *
from tool import *


class MarkdownPattern(object):

    def __init__(self, name=''):
        self.origin = ''
        self.name = name
        self.match = ''
        self.replace = ''
        self.args = []
        self.replace_backup = None
        self.function = None

    def __str__(self):
        return self.name

    def init(self):

        pattern = self.origin.strip('\n').split('\n')
        line_index = pattern[0]
        line_match = pattern[1]
        line_index = line_index.rstrip()
        line_match = line_match.rstrip()
        line_index = line_index + (" " * (len(line_match) - len(line_index)))

        self.match = line_match

        start = None
        end = None

        result = []

        for index, value in enumerate(list(line_index)):
            if value in string.digits:
                if start is None:
                    start = index
                elif end is None:
                    end = index

            if index == len(line_index) - 1:
                end = index + 1

            if start is not None and end is not None:
                item = line_index[start:end].strip().split()
                if len(item) == 1:
                    item = item + ['']
                arg_index, arg_name = item
                arg_index = int(arg_index)
                arg_value = line_match[start:end]
                arg_value = arg_value.replace(r'(?<=\n)', '')
                arg_value = arg_value.replace(r'(?=\n)', '')

                arg = Arg(index=arg_index, name=arg_name, value=arg_value)
                result.append(arg)

                start = index
                end = None

        self.args = result

    def debug(self):
        print()
        print(self.name)
        print(self.origin)
        for arg in self.args:
            print(arg)

    def get_arg_index(self, arg_name):
        index = 0
        arg: Arg
        for arg in self.args:
            if arg.name == arg_name:
                index = arg.index
                break
        # arg start with 1
        index = index - 1
        return index

    def get_match_replace(self, match: re.Match):
        if not self.replace_backup:
            self.replace_backup = self.replace
        self.replace = copy.copy(self.replace_backup)

        self.replace = self.replace.replace('\\n', '\n')
        for index in range(30, 0, -1):
            item = f'\\{index}'
            if item not in self.replace:
                continue
            self.replace = self.replace.replace(item, match.groups()[index - 1])

        if self.function:
            result = self.function(self, match)
            self.replace = self.replace.format(**result)
        return self.replace


################################################################################

patterns = []

################################################################################

# <!-- [center] -->
pattern_center = MarkdownPattern('[center]')
patterns.append(pattern_center)
pattern_center.origin = r"""
       1     2   3           4   5          6                7 
(?<=\n)(<!--)(\s)(\[center\])(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_center.replace = r"\1\2\3\4\5" \
                         r"\n<div style='text-align:center'>" \
                         r"\n\6\n" \
                         r"</div>\n" \
                         r"\7"

# --------------------------------------------------------------------------------

# <!-- [left] -->
pattern_left = MarkdownPattern('[left]')
patterns.append(pattern_left)
pattern_left.origin = r"""
       1     2   3         4   5          6                7 
(?<=\n)(<!--)(\s)(\[left\])(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_left.replace = r"\1\2\3\4\5" \
                       r"\n<div style='float:left;width:calc(50% - 5px);'>" \
                       r"\n\6\n" \
                       r"</div>\n" \
                       r"\7"

# --------------------------------------------------------------------------------

# <!-- [right] -->
pattern_right = MarkdownPattern('[right]')
patterns.append(pattern_right)
pattern_right.origin = r"""
       1     2   3          4   5          6                7 
(?<=\n)(<!--)(\s)(\[right\])(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_right.replace = r"\1\2\3\4\5" \
                        r"\n<div style='float:right;width:calc(50% - 5px);'>" \
                        r"\n\6\n" \
                        r"</div>\n" \
                        r"\7"

# --------------------------------------------------------------------------------

# <!-- [clear] -->
pattern_clear = MarkdownPattern('[clear]')
patterns.append(pattern_clear)
pattern_clear.origin = r"""
       1     2   3          4   5          6                7 
(?<=\n)(<!--)(\s)(\[clear\])(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_clear.replace = r"\1\2\3\4\5" \
                        r"\n<div style='clear:both'>" \
                        r"\6" \
                        r"</div>\n" \
                        r"\7"

# --------------------------------------------------------------------------------

# 插入全部 代码块
# <!-- xxx.py -->
# <!-- xxx.css -->
# <!-- xxx.js -->
# <!-- xxx.json -->
# <!-- xxx.md -->
# <!-- xxx.html -->
pattern_code = MarkdownPattern('code')
patterns.append(pattern_code)
pattern_code.origin = rf"""
       1     2   3 file                 {re_code_len}  4   5          6                7     
(?<=\n)(<!--)(\s)((?:[\w\d\/]+)(?:\.)(?:{re_code_str}))(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_code.replace = r'\1\2\3\4\5\n' \
                       r'```{type}\n' \
                       r'{code}\n' \
                       r'```\n' \
                       r'\7'


def get_type_code(self: MarkdownPattern, match: re.Match):
    index_file = self.get_arg_index('file')

    file = match.groups()[index_file] if index_file >= 0 else ''

    file_type = os.path.splitext(file)[-1]
    file_type = file_type.replace('.', '')

    file_full_path = get_file_path(file)
    code = open_file(file_full_path)

    return {'type': file_type, 'code': code}


pattern_code.function = get_type_code

# --------------------------------------------------------------------------------

# 插入全部 代码块 carbon
# <!-- xxx.py carbon -->
pattern_carbon = MarkdownPattern('carbon')
patterns.append(pattern_carbon)
pattern_carbon.origin = rf"""
       1     2   3 file                 {re_code_len}  4   5       6   7          8                9     
(?<=\n)(<!--)(\s)((?:[\w\d\/]+)(?:\.)(?:{re_code_str}))(\s)(carbon)(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_carbon.replace = r'\1\2\3\4\5\6\7\n' \
                         r'<iframe\n' \
                         r'    src="{src}"\n' \
                         r'    width="100%" height="100%"\n' \
                         r'    style="width:{width}px; height:{height}px; border:0; overflow:hidden;"\n' \
                         r'    sandbox="allow-scripts allow-same-origin">\n' \
                         r'</iframe>\n' \
                         r'\9'


def get_carbon_arg(self: MarkdownPattern, match: re.Match):
    index_file = self.get_arg_index('file')
    file = match.groups()[index_file] if index_file >= 0 else ''
    file_full_path = get_file_path(file)

    with open(file_full_path, 'r', encoding='utf-8') as file:
        code = file.readlines()

    width = 0
    height = 0

    for item in code:
        width = len(item) if len(item) > width else width
        height += 1

    font_size = carbon.get('fontSize')
    font_size = font_size.replace('px', '')
    font_size = int(font_size)

    line_height = carbon.get('lineHeight')
    line_height = line_height.replace('%', '')
    line_height = int(line_height) / 100

    # 边框
    padding_vertical = carbon.get('paddingVertical')
    padding_vertical = padding_vertical.replace('px', '')
    padding_vertical = int(padding_vertical)
    padding_horizontal = carbon.get('paddingHorizontal')
    padding_horizontal = padding_horizontal.replace('px', '')
    padding_horizontal = int(padding_horizontal)

    # 行高
    height = height * font_size * line_height * 1.25
    height = math.ceil(height)
    height = height + padding_vertical + padding_vertical

    # 行宽
    width = width * 10 + 10
    width = width + padding_horizontal + padding_horizontal

    # 代码
    code = ''.join(code)
    code = quote(quote(code))

    # url编码
    config = {}
    for key, value in carbon.items():
        # 125%
        if key == 'lineHeight':
            value = line_height
        key = carbon_args.get(key)
        if not key:
            continue
        config[key] = value
    args = [f"{key}={value}".lower() for key, value in config.items()]
    args = '&'.join(args)
    src = f"https://carbon.now.sh/embed/?{args}&code={code}"

    return {'src': src, 'width': width, 'height': height}


pattern_carbon.function = get_carbon_arg

# --------------------------------------------------------------------------------

# 代码块运行
# <!-- xxx.py cmd:D:\Python\_python_\Scripts\python.exe -->
pattern_code_run = MarkdownPattern('code-run')
patterns.append(pattern_code_run)
pattern_code_run.origin = rf"""
       1     2   3 file                 {re_code_len}  4   5     6 cmd     7   8          9                10   
(?<=\n)(<!--)(\s)((?:[\w\d\/]+)(?:\.)(?:{re_code_str}))(\s)(cmd:)([\s\S]+?)(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_code_run.replace = r'\1\2\3\4\5\6\7\8\n' \
                           r'```\n' \
                           r'{result}\n' \
                           r'```\n' \
                           r'\10'


def get_code_run_result(self: MarkdownPattern, match: re.Match):
    index_file = self.get_arg_index('file')
    index_cmd = self.get_arg_index('cmd')

    file = match.groups()[index_file] if index_file >= 0 else ''
    cmd = match.groups()[index_cmd] if index_cmd >= 0 else ''

    file_full_path = get_file_path(file)

    # D:\Python\_python_\Scripts\python.exe
    command = f"{cmd} {file_full_path}"

    # 运行结果
    result = subprocess.getoutput(command)

    return {'result': result}


pattern_code_run.function = get_code_run_result

# --------------------------------------------------------------------------------

# <!-- xxx.py 1:2 -->
# <!-- xxx.py 1:-2 -->
pattern_code_slice = MarkdownPattern('code-slice')
patterns.append(pattern_code_slice)
pattern_code_slice.origin = rf"""
       1     2   3 file                 {re_code_len}  4   5 arg          6   7          8                9    
(?<=\n)(<!--)(\s)((?:[\w\d\/]+)(?:\.)(?:{re_code_str}))(\s)([-\d]+:[-\d]+)(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_code_slice.replace = r'\1\2\3\4\5\6\7\n' \
                             r'```{type}\n' \
                             r'{code}\n' \
                             r'```\n' \
                             r'\9'


def get_type_code_slice(self: MarkdownPattern, match: re.Match):
    index_file = self.get_arg_index('file')
    index_arg = self.get_arg_index('arg')

    file = match.groups()[index_file] if index_file >= 0 else ''
    arg = match.groups()[index_arg] if index_arg >= 0 else ''

    file_type = os.path.splitext(file)[-1]
    file_type = file_type.replace('.', '')

    file_full_path = get_file_path(file)

    # 1:2
    # 1:-1
    arg = arg.split(":")
    _start_ = arg[0]
    _end_ = arg[1]
    _start_ = try_str_to_num(_start_)
    _end_ = try_str_to_num(_end_)
    command = {'start': _start_, 'end': _end_}
    code = open_file(file_full_path, command)

    return {'type': file_type, 'code': code}


pattern_code_slice.function = get_type_code_slice

# --------------------------------------------------------------------------------

# <!-- xxx.py function:test --> 代码块\函数
pattern_code_function = MarkdownPattern('code-function')
patterns.append(pattern_code_function)
pattern_code_function.origin = rf"""
       1     2   3 file                 {re_code_len}  4   5 arg         6   7          8                9    
(?<=\n)(<!--)(\s)((?:[\w\d\/]+)(?:\.)(?:{re_code_str}))(\s)(function:\w+)(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_code_function.replace = r'\1\2\3\4\5\6\7\n' \
                                r'```{type}\n' \
                                r'{code}\n' \
                                r'```\n' \
                                r'\9'


def get_type_code_function(self: MarkdownPattern, match: re.Match):
    index_file = self.get_arg_index('file')
    index_arg = self.get_arg_index('arg')

    file = match.groups()[index_file] if index_file >= 0 else ''
    arg = match.groups()[index_arg] if index_arg >= 0 else ''

    file_type = os.path.splitext(file)[-1]
    file_type = file_type.replace('.', '')

    file_full_path = get_file_path(file)

    # function:test
    arg = arg.split(":")
    command = {arg[0]: arg[-1]}
    code = open_file(file_full_path, command)

    return {'type': file_type, 'code': code}


pattern_code_function.function = get_type_code_slice

# --------------------------------------------------------------------------------

# <!-- xxx.py label:test --> 代码块\函数
pattern_label = MarkdownPattern('label')
patterns.append(pattern_label)
pattern_label.origin = rf"""
       1     2   3 file                 {re_code_len}  4   5 arg               6   7          8                9    
(?<=\n)(<!--)(\s)((?:[\w\d\/]+)(?:\.)(?:{re_code_str}))(\s)(label:[\w\d\s#:-]+)(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_label.replace = r'\1\2\3\4\5\6\7\n' \
                        r'```{type}\n' \
                        r'{code}\n' \
                        r'```\n' \
                        r'\9'


def get_label_code(self: MarkdownPattern, match: re.Match):
    index_file = self.get_arg_index('file')
    index_arg = self.get_arg_index('arg')

    file = match.groups()[index_file] if index_file >= 0 else ''
    arg = match.groups()[index_arg] if index_arg >= 0 else ''

    file_type = os.path.splitext(file)[-1]
    file_type = file_type.replace('.', '')

    file_full_path = get_file_path(file)

    # label:test
    arg = arg.split(":")
    command = {arg[0]: arg[-1]}
    code = open_file(file_full_path, command)

    return {'type': file_type, 'code': code}


pattern_label.function = get_label_code

# --------------------------------------------------------------------------------

# <!-- xxx.py origin:label:test --> 原始代码块\函数
pattern_label_origin = MarkdownPattern('label-origin')
patterns.append(pattern_label_origin)
pattern_label_origin.origin = rf"""
       1     2   3 file                 {re_code_len}  4   5 arg                      6   7          8                9    
(?<=\n)(<!--)(\s)((?:[\w\d\/]+)(?:\.)(?:{re_code_str}))(\s)(origin:label:[\w\d\s#:-]+)(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_label_origin.replace = r'\1\2\3\4\5\6\7\n{code}\n\9'


def get_label_code_origin(self: MarkdownPattern, match: re.Match):
    index_file = self.get_arg_index('file')
    index_arg = self.get_arg_index('arg')

    file = match.groups()[index_file] if index_file >= 0 else ''
    arg = match.groups()[index_arg] if index_arg >= 0 else ''

    file_type = os.path.splitext(file)[-1]
    file_type = file_type.replace('.', '')

    file_full_path = get_file_path(file)

    # origin:label:test
    arg = arg.lstrip('origin:')
    arg = arg.split(":")
    command = {arg[0]: arg[-1]}
    code = open_file(file_full_path, command)

    return {'type': file_type, 'code': code}


pattern_label_origin.function = get_label_code_origin

# --------------------------------------------------------------------------------

# 插入全部 原始文件
# <!-- xxx.py origin -->
pattern_origin = MarkdownPattern('origin')
patterns.append(pattern_origin)
pattern_origin.origin = r"""
       1     2   3 file       4   5       6   7          8 code           9     
(?<=\n)(<!--)(\s)([\w\d\.\/]+)(\s)(origin)(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_origin.replace = r"\1\2\3\4\5\6\7\n{data}\n\9"


def get_origin_file(self: MarkdownPattern, match: re.Match):
    index_file = self.get_arg_index('file')
    file = match.groups()[index_file] if index_file >= 0 else ''

    file_full_path = get_file_path(file)
    data = open_file(file_full_path)

    return {'data': data}


pattern_origin.function = get_origin_file

# --------------------------------------------------------------------------------

# 插入全部 原始文件
# <!-- xxx.py origin:1:2 -->
pattern_origin_slice = MarkdownPattern('origin-slice')
patterns.append(pattern_origin_slice)
pattern_origin_slice.origin = r"""
       1     2   3 file       4   5 arg                 6   7          8 code           9     
(?<=\n)(<!--)(\s)([\w\d\.\/]+)(\s)(origin:[-\d]+:[-\d]+)(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_origin_slice.replace = r"\1\2\3\4\5\6\7\n{data}\n\9"


def get_origin_file_slice(self: MarkdownPattern, match: re.Match):
    index_file = self.get_arg_index('file')
    index_arg = self.get_arg_index('arg')
    file = match.groups()[index_file] if index_file >= 0 else ''
    arg = match.groups()[index_arg] if index_arg >= 0 else ''

    # origin:1:2
    arg = arg.split(":")
    _ = arg[0]
    _start_ = arg[1]
    _end_ = arg[2]
    _start_ = try_str_to_num(_start_)
    _end_ = try_str_to_num(_end_)
    command = {'start': _start_, 'end': _end_}

    file_full_path = get_file_path(file)
    data = open_file(file_full_path, command)

    return {'data': data}


pattern_origin_slice.function = get_origin_file_slice

# --------------------------------------------------------------------------------

# 图片基础
# <!-- xxx.png -->
pattern_image_md = MarkdownPattern('image-md')
patterns.append(pattern_image_md)
pattern_image_md.origin = rf"""
       1     2   3 file                 {re_image_len}  4   5          6                7  
(?<=\n)(<!--)(\s)((?:[\w\d\/]+)(?:\.)(?:{re_image_str}))(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_image_md.replace = r'\1\2\3\4\5' \
                           r'\n![\3](\3)\n' \
                           r'\7'

# --------------------------------------------------------------------------------


# 图片\比例
# <!-- xxx.png 0.2x0.5 --> 图片\比例
# <!-- xxx.png 20x50 --> 图片\宽高
pattern_image_html = MarkdownPattern('image-html')
patterns.append(pattern_image_html)
pattern_image_html.origin = fr"""
       1     2   3 file               {re_image_len}  4   5 arg            6   7          8                9
(?<=\n)(<!--)(\s)((?:[\w\d]+)(?:\.)(?:{re_image_str}))(\s)([\d\.]+x[\d\.]+)(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_image_html.replace = r"\1\2\3\4\5\6\7" \
                             r"\n<img src='\3' style='width:{width}; height:{height};' alt='\3'>\n" \
                             r"\9"


def get_w_h(self: MarkdownPattern, match: re.Match):
    index_arg = self.get_arg_index('arg')
    arg = match.groups()[index_arg] if index_arg >= 0 else ''

    width = 1
    height = 1

    # 0.2x0.3
    # 100x100
    # 图片长宽 width x height

    w, h = arg.split('x')
    width = try_str_to_num(w)
    height = try_str_to_num(h)

    # 0.5
    if width <= 1:
        width = f"{width * 100}%"
    else:
        width = f"{width}px"

    # 500
    if height <= 1:
        height = f"{height * 100}%"
    else:
        height = f"{height}px"

    return {'width': width, 'height': height}


pattern_image_html.function = get_w_h

# --------------------------------------------------------------------------------

# <!-- py.py {start:1 end:3} -->
# <!-- py.py {cmd:D:\Python\_python_\Scripts\python.exe type:txt} -->
# <!-- xxx.png {width:0.1 height:0.3 alt:xxx} -->
# <!-- xxx.png {width:200 height:300 alt:xxx} -->
pattern_command = MarkdownPattern('cmd')
patterns.append(pattern_command)
pattern_command.origin = r"""
       1     2   3 file      4   5 arg         6   7          8 code           9
(?<=\n)(<!--)(\s)([\w\d\./]+)(\s)(\{[\s\S]+?\})(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_command.replace = r'\1\2\3\4\5\6\7\8\9'


def get_command(self: MarkdownPattern, match: re.Match):
    index_file = self.get_arg_index('file')
    index_arg = self.get_arg_index('arg')
    file = match.groups()[index_file] if index_file >= 0 else ''
    arg = match.groups()[index_arg] if index_arg >= 0 else ''

    file_full_path = get_file_path(file)

    # {start:1 end:3}
    # k:v命令
    command = {}
    arg = arg.lstrip("{").rstrip("}").strip()
    arg = arg.split(" ")
    for o in arg:
        k, v = o.split(':', 1)
        v = str_to_bool(v)
        v = try_str_to_num(v) if not isinstance(v, bool) else v
        command[k] = v

    data = open_file(file_full_path, command)

    return {'data': data, 'command': command}


################################################################################


for item in patterns:
    item.init()

if __name__ == '__main__':
    # pattern_code_function.debug()
    pattern_image_html.debug()
