import os
import re
import sys
import subprocess
from pathlib import WindowsPath

# --------------------------------------------------------------------------------

path = WindowsPath(r"D:\#Bin\KubeCTL.exe")
result = subprocess.Popen(f"{path} version", shell=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
result = result.stdout.read().decode()
version = re.search("([\d.]+)", result).group(0)
with open(path.with_name(f"{path.stem}_{version}"), "w+") as file:
    file.write("")
print(f"{path} {version}\n")

# --------------------------------------------------------------------------------

path = WindowsPath(r"D:\#Bin\MiniKube.exe")
result = subprocess.Popen(f"{path} version", shell=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
result = result.stdout.read().decode()
version = re.search("([\d.]+)", result).group(0)
with open(path.with_name(f"{path.stem}_{version}"), "w+") as file:
    file.write("")
print(f"{path} {version}\n")

# --------------------------------------------------------------------------------

path = WindowsPath(r"D:\#Bin\RePKG.exe")
result = subprocess.Popen(f"{path} version", shell=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
result = result.stderr.read().decode()
version = re.search("([\d.]+)", result).group(0)
with open(path.with_name(f"{path.stem}_{version}"), "w+") as file:
    file.write("")
print(f"{path} {version}\n")