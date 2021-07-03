import inspect
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
from urllib.parse import quote, unquote, urlencode

from markdown import *


def test_pattern_change(pattern, markdown):
    if not markdown.startswith('\n'):
        markdown = '\n' + markdown
    if not markdown.endswith('\n'):
        markdown = markdown + '\n'

    result = []
    for line in markdown.split('\n'):
        if line.startswith('    '):
            line = line.lstrip('    ')
        result.append(line)
    markdown = '\n'.join(result)

    pattern.debug()
    markdown = re.sub(pattern.match, pattern.get_match_replace, markdown)
    print(markdown)


def test_code():
    markdown = r"""
    <!-- py.py -->
    <!--  -->
    """
    from pattern import pattern_code as mdp
    test_pattern_change(mdp, markdown)


def test_code_slice():
    markdown = r"""
    <!-- py.py 2:7 -->
    <!--  -->
    """
    from pattern import pattern_code_slice as mdp
    test_pattern_change(mdp, markdown)


def test_code_function():
    markdown = r"""
    <!-- py.py function:test_set -->
    <!--  -->
    """
    from pattern import pattern_code_function as mdp
    test_pattern_change(mdp, markdown)


def test_code_run():
    markdown = r"""
    <!-- py.py cmd:D:\Python\_python_\Scripts\python.exe -->
    <!--  -->
    """
    from pattern import pattern_code_run as mdp
    test_pattern_change(mdp, markdown)


def test_carbon():
    markdown = r"""
    <!-- py.py carbon -->
    <!--  -->
    """
    from pattern import pattern_carbon as mdp
    test_pattern_change(mdp, markdown)


def test_origin():
    markdown = r"""
    <!-- config.py origin -->
    <!--  -->
    """
    from pattern import pattern_origin as mdp
    test_pattern_change(mdp, markdown)


def test_origin_slice():
    markdown = r"""
    <!-- config.py origin:3:9 -->
    <!--  -->
    """
    from pattern import pattern_origin_slice as mdp
    test_pattern_change(mdp, markdown)


def test_image_md():
    markdown = r"""
    <!-- png.png -->
    <!--  -->
    """
    from pattern import pattern_image_md as mdp
    test_pattern_change(mdp, markdown)


def test_image_html():
    markdown = r"""
    <!-- png.png 0.2x0.2 -->
    <!--  -->
    """
    from pattern import pattern_image_html as mdp
    test_pattern_change(mdp, markdown)


def test_label():
    markdown = r"""
    <!-- config.py label:# test -->
    <!--  -->
    """
    from pattern import pattern_label as mdp
    test_pattern_change(mdp, markdown)


def test_label_origin():
    markdown = r"""
    <!-- config.py origin:label:# test -->
    <!--  -->
    """
    from pattern import pattern_label_origin as mdp
    test_pattern_change(mdp, markdown)


def test_left_right_clear():
    markdown = r"""
    <!-- [left] -->
    <!-- png.png -->
    <!--  -->

    <!-- [right] -->
    <!-- png.png -->
    <!--  -->

    <!-- [clear] -->
    <!--  -->
    """
    from pattern import pattern_left as mdp
    test_pattern_change(mdp, markdown)

    from pattern import pattern_right as mdp
    test_pattern_change(mdp, markdown)

    from pattern import pattern_clear as mdp
    test_pattern_change(mdp, markdown)


def test_center():
    markdown = r"""
    <!-- [center] -->
    <!-- png.png -->
    <!--  -->
    """
    from pattern import pattern_center as mdp
    test_pattern_change(mdp, markdown)
    from pattern import pattern_image_md as mdp
    test_pattern_change(mdp, markdown)


def test_re():
    markdown = r"""

    <!-- [center] -->
    <!--  -->

    """
    markdown = markdown.replace('    ', '')

    rule = r"(?<=\n)(<!--)(\s)(\[center\])(\s)(-->)(?=\n)([\s\S]+?)(?<=\n)(<!--\s+-->)(?=\n)"

    result = re.findall(rule, markdown)

    for item in result:
        print(item)


def test_main():
    files = get_markdown_files('md.md')

    for file in files:
        file_preview = get_new_file_path(file)
        if os.path.isfile(file_preview):
            print(f'remove {file_preview}')
            os.remove(file_preview)

    print()

    # for file in files:
    #     markdown = get_markdown(file)
    #     markdown = change_markdown(markdown)
    #     file_preview = save_markdown(markdown, file)
    #     print(f'create {file_preview}')


if __name__ == '__main__':
    print()
    # test_center()
    # test_markdown_args()
    # test_change()
    # test_float()
    # test_code_result()
    # test_re()
    # test_code()
    # test_code_origin()
    # test_image_md()
    # test_image_html()
    # test_code_slice()
    # test_code_function()
    # test_code_origin_slice()
    # test_label_origin()
    # test_run_code()
    # test()
    # test_carbon()
