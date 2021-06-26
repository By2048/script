import os
import re
from pprint import pprint
import copy
import doctest
import string
from collections import namedtuple
from enum import Enum
import subprocess
from pathlib import Path

# from .markdown import *
from markdown import *


def test_markdown_args():
    markdown = r"""

    <!-- md1.md origin -->
    <!--  -->
    
    <!-- xxx.py 1:2 -->
    <!--  -->
    
    <!-- xxx.py 1:-2 -->
    <!--  -->
    
    <!-- xxx.py function:test -->
    <!--  -->
    
    <!-- xxx.py label:test -->
    <!--  -->
    
    <!-- xxx.py origin -->
    <!--  -->
    
    <!-- xxx.py origin:1:2 -->
    <!--  -->
    
    <!-- xxx.png 0.2x0.5 -->
    <!--  -->
    
    <!-- xxx.png 20x50 -->
    <!--  -->
    
    """

    markdown = markdown.replace('    ', '')

    pattern: MarkdownPattern
    for pattern in patterns:
        result = re.findall(pattern.match, markdown)
        if not result:
            continue
        for item in result:
            index_file = pattern.get_arg_index('file')
            index_arg = pattern.get_arg_index('arg')
            file = item[index_file] if index_file >= 0 else ''
            arg = item[index_arg] if index_arg >= 0 else ''
            cmd = change(arg)
            print()
            print(file, arg)
            print(cmd)
            # pattern_replace = pattern.get_replace_pattern(file, cmd)
            # markdown = re.sub(pattern.match, pattern_replace, markdown)


def test_change():
    markdown = r"""
    
    <!-- md1.md origin -->
    <!--  -->
    
    """
    markdown = markdown.replace('    ', '')
    markdown = change_markdown(markdown)
    print(markdown)


def test_float():
    markdown = r"""

    <!-- [left] -->
    <!-- png.png -->
    <!--  -->
    
    <!-- [right] -->
    <!-- png.png -->
    <!--  -->
    
    <!-- [clear] -->
    <!--  -->

    """.replace('    ', '')
    markdown = change_markdown(markdown)
    print(markdown)


def test_code_result():
    markdown = r"""

    <!-- py.py {cmd:D:\Python\_python_\Scripts\python.exe type:txt} -->
    <!--  -->

    """
    markdown = markdown.replace('    ', '')
    markdown = change_markdown(markdown)
    print(markdown)


def main():
    files = get_markdown_files('md.md')

    for file in files:
        file_preview = get_new_file_path(file)
        if os.path.isfile(file_preview):
            print(f'remove {file_preview}')
            os.remove(file_preview)

    print()

    for file in files:
        markdown = get_markdown(file)
        markdown = change_markdown(markdown)
        file_preview = save_markdown(markdown, file)
        print(f'create {file_preview}')


def test_re():
    markdown = r"""

    <!-- py.py -->
    <!--  -->

    """
    markdown = markdown.replace('    ', '')

    pattern: MarkdownPattern
    for pattern in patterns:
        markdown = re.sub(pattern.match, pattern.get_match_replace, markdown)

    print(markdown)


if __name__ == '__main__':
    # print()
    # test_markdown_args()
    # test_change()
    # test_float()
    # test_code_result()
    test_re()
    # test()
    # main()
