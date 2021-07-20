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
