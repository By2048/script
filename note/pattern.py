import os
import re
import copy
import string
import subprocess

from config import *
from tool import *


class MarkdownPattern(object):

    def __init__(self):
        self._origin_ = ''
        self.match = ''
        self.args = []
        self.replace_base = ''
        self.replace_code = ''
        self.replace_file = ''
        self.replace_backup = []

    @property
    def origin(self):
        return self._origin_

    @origin.setter
    def origin(self, data):
        self._origin_ = data
        self.match = self.get_index_match()[-1]
        self.args = self.get_args()

    def __str__(self):
        return f'{self.match}'

    def get_index_match(self):
        pattern = self.origin.strip('\n').split('\n')
        line_index = pattern[0]
        line_match = pattern[1]
        line_index = line_index.strip()
        line_match = line_match.strip()
        line_index = line_index + (" " * (len(line_match) - len(line_index)))
        return line_index, line_match

    def get_args(self):

        line_index, line_match = self.get_index_match()

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
                end = index

            if start is not None and end is not None:
                arg_index = line_index[start:end].strip()
                item = arg_index.strip().split()
                if len(item) == 1:
                    item = item + ['']
                arg_index, arg_name = item
                arg_index = int(arg_index)
                arg_value = line_match[start:end]

                arg = Arg(index=arg_index, name=arg_name, value=arg_value)
                result.append(arg)

                start = index
                end = None

        return result

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

    def init_replace_item(self, match: re.Match):
        if not self.replace_backup:
            self.replace_backup = [self.replace_base, self.replace_code, self.replace_file]
        replace_result = copy.copy(self.replace_backup)
        self.replace_base, self.replace_code, self.replace_file = replace_result
        for replace_index, replace_item in enumerate(replace_result):
            replace_item = replace_item.replace('\\n', '\n')
            for index in range(1, 30):
                item = f'\\{index}'
                if item not in self.replace_base:
                    continue
                replace_item = replace_item.replace(item, match.groups()[index - 1])
            replace_result[replace_index] = replace_item
        self.replace_base, self.replace_code, self.replace_file = replace_result

    def get_replace_pattern(self, file=None, cmd: dict = None):
        # path  file relative path

        # [center]类型的指令
        if not file and not cmd:
            return self.replace_base

        file_name = os.path.basename(file)
        file_type = os.path.splitext(file)[-1]

        file_relative_path = file
        file_full_path = get_file_path(file)

        file_type = file_type.replace('.', '')

        # 处理代码 \ 文件内容
        if file_type in types_code:

            if 'cmd' in cmd.keys():
                # 运行结果
                code = subprocess.getoutput(f"{cmd['cmd']} {file_full_path}")
            else:
                # 代码内容
                code = open_file(file_full_path, cmd)

            pattern_replace = self.replace_base

            # file 原始文件内容
            if cmd.get('origin') is True:
                pattern_replace = self.replace_file.replace('{file}', code)

            # code Markdown代码块
            if cmd.get('origin') in [False, None]:
                pattern_replace = self.replace_code \
                    .replace('{code}', code) \
                    .replace('{type}', file_type)

            return pattern_replace

        # 处理图片
        if file_type in types_image:

            result = ''

            if not cmd:
                result = f"![{file_name}]({file_relative_path})"

            if cmd:
                width = cmd.get('width')
                height = cmd.get('height')

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

                style = f"width:{width}; height:{height};"
                result = f"<img src='{file_relative_path}' style='{style}' alt='{file}'>"

            if result:
                return self.replace_file.replace("{file}", result)

        return self.replace_base

    def get_match_replace(self, match: re.Match):
        self.init_replace_item(match)
        index_file = self.get_arg_index('file')
        index_arg = self.get_arg_index('arg')
        file = match.groups()[index_file] if index_file >= 0 else ''
        arg = match.groups()[index_arg] if index_arg >= 0 else ''
        cmd = change(arg)
        replace_pattern = self.get_replace_pattern(file, cmd)
        replace_data = replace_pattern
        return replace_data


################################################################################

# <!-- [center] -->
pattern_center = MarkdownPattern()
pattern_center.origin = r"""
1            2   3           4   5          6         7 
(?<=\n)(<!--)(\s)(\[center\])(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_center.replace_base = r"\1\2\3\4\5" \
                              r"\n<div style='text-align:center'>" \
                              r"\n\6\n" \
                              r"</div>\n" \
                              r"\7"

# <!-- [left] -->
pattern_left = MarkdownPattern()
pattern_left.origin = r"""
1            2   3         4   5          6         7 
(?<=\n)(<!--)(\s)(\[left\])(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_left.replace_base = r"\1\2\3\4\5" \
                            r"\n<div style='float:left;width:calc(50% - 5px);'>" \
                            r"\n\6\n" \
                            r"</div>\n" \
                            r"\7"

# <!-- [right] -->
pattern_right = MarkdownPattern()
pattern_right.origin = r"""
1            2   3          4   5          6         7 
(?<=\n)(<!--)(\s)(\[right\])(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_right.replace_base = r"\1\2\3\4\5" \
                             r"\n<div style='float:right;width:calc(50% - 5px);'>" \
                             r"\n\6\n" \
                             r"</div>\n" \
                             r"\7"

# <!-- [clear] -->
pattern_clear = MarkdownPattern()
pattern_clear.origin = r"""
1            2   3          4   5          6         7 
(?<=\n)(<!--)(\s)(\[clear\])(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_clear.replace_base = r"\1\2\3\4\5" \
                             r"\n<div style='clear:both'>" \
                             r"\6" \
                             r"</div>\n" \
                             r"\7"

# 插入全部 代码块
# <!-- xxx.py -->
# <!-- xxx.css -->
# <!-- xxx.js -->
# <!-- xxx.json -->
# <!-- xxx.md -->
# <!-- xxx.html -->
# <!-- xxx.png -->
# <!-- xxx.csv -->
pattern_base = MarkdownPattern()
pattern_base.origin = r"""
1            2   3 file      4   5          6 code    7     
(?<=\n)(<!--)(\s)([\w\d\./]+)(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_base.replace_base = r'\1\2\3\4\5\6\7'
pattern_base.replace_file = r"\1\2\3\4\5\n{file}\n\7"
pattern_base.replace_code = r'\1\2\3\4\5\n' \
                            r'```{type}\n' \
                            r'{code}\n' \
                            r'```\n' \
                            r'\7'

# <!-- xxx.py 1:2 --> 代码块
# <!-- xxx.py 1:-2 --> 代码块
# <!-- xxx.py function:test --> 代码块\函数
# <!-- xxx.py label:test --> 代码块\标签
# <!-- xxx.py origin --> 读取内容直接插入
# <!-- xxx.py origin:1:2 --> 读取内容直接插入
# <!-- xxx.png 0.2x0.5 --> 图片\比例
# <!-- xxx.png 20x50 --> 图片\宽高
pattern_quick = MarkdownPattern()
pattern_quick.origin = r"""
1            2   3 file      4   5 arg          6   7          8 code    9   
(?<=\n)(<!--)(\s)([\w\d\./]+)(\s)([\w\d\.\-:x]+)(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_quick.replace_base = r'\1\2\3\4\5\6\7\8\9'
pattern_quick.replace_file = r"\1\2\3\4\5\6\7\n{file}\n\9"
pattern_quick.replace_code = r'\1\2\3\4\5\6\7\n' \
                             r'```{type}\n' \
                             r'{code}\n' \
                             r'```\n' \
                             r'\9'

# <!-- py.py {start:1 end:3} -->
# <!-- py.py {cmd:D:\Python\_python_\Scripts\python.exe type:txt} -->
# <!-- xxx.png {width:0.1 height:0.3 alt:xxx} -->
# <!-- xxx.png {width:200 height:300 alt:xxx} -->
pattern_command = MarkdownPattern()
pattern_command.origin = r"""
1            2   3 file      4   5 arg         6   7          8 code    9   
(?<=\n)(<!--)(\s)([\w\d\./]+)(\s)(\{[\s\S]+?\})(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)
"""
pattern_command.replace_base = r'\1\2\3\4\5\6\7\8\9'
pattern_command.replace_file = r"\1\2\3\4\5\6\7\n{file}\n\9"
pattern_command.replace_code = r'\1\2\3\4\5\6\7\n' \
                               r'```{type}\n' \
                               r'{code}\n' \
                               r'```\n' \
                               r'\9'

################################################################################

patterns = [
    pattern_command,
    pattern_quick,
    pattern_base,
    pattern_center,
    pattern_left,
    pattern_right,
    pattern_clear,
]
