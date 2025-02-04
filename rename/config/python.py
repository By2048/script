from .base import capitalize

config_python = [
    # pattern.cpython-37.pyc
    [r"(\w+)(\.cpython-37)(\.pyc)", r"\1\3"],
    # python-x.x.x.exe
    [r"(python)(-)([\d\.]+)(.exe)", (r"\1_\3\4", capitalize)],
    # python-x.x.x-amd64.exe
    [r"(python)(-)([\d\.]+)(-amd64)(.exe)", (r"\1_\3\5", capitalize)],
    # python-x.x.x-embed-amd64.zip
    [r"(python)(-)([\d\.]+)(-embed)(-amd64)(.zip)", (r"\1_\3\5\4\6", capitalize)],
    # python-3.9.9-embed-win32.zip
    [r"(python)(-)([\d\.]+)(-embed)(-win32)(.zip)", (r"\1_\3\5\4\6", capitalize)],
]