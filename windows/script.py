from model import Script
from config import console
from config import windows_config, scripts
from config import path_script, path_script_txt

from rich.panel import Panel
from rich.align import Align


def init_scripts():
    for script_sub_folder in windows_config.get("@Script").keys():
        config_items = windows_config["@Script"][script_sub_folder].items()
        for script_name, script_args in config_items:
            script = Script()

            if not script_args:
                scripts.append(script)
                continue

            exe = script_args.get("Exe") or ""
            args = script_args.get("Args") or []
            before = script_args.get("Before") or []
            after = script_args.get("After") or []
            commands = script_args.get("Commands") or []
            args = [args] if not isinstance(args, list) else args
            before = [before] if not isinstance(before, list) else before
            after = [after] if not isinstance(after, list) else after
            commands = [commands] if not isinstance(commands, list) else commands

            script.exe = exe
            script.args = args
            script.before = before
            script.after = after
            script.commands = commands
            script.type = script_args.get("Type") or "Bat"
            if script.type == "Bat":
                script.path = path_script / script_sub_folder / f"{script_name}.bat"
            if script.type == "PowerShell":
                script.path = path_script / script_sub_folder / f"{script_name}.ps1"
            if script:
                scripts.append(script)


def create_script_bat_file(script):
    code = "@Echo Off\n\n"
    code += "SetLocal\n\n"

    if script.before:
        for before in script.before:
            code += f"{before}\n"
        code += "\n"

    if script.exe:
        code += f"Set Exe=\"{script.exe}\"\n"
        if not script.args or len(script.args) == 0:
            code += f"\n%Exe%  %*\n\n"
        elif len(script.args) == 1:
            code += f"Set Arg=\"{script.args[0]}\"\n\n"
            code += f"%Exe%  %Arg%  %*\n\n"
        elif len(script.args) > 1:
            for index, arg in enumerate(script.args, start=1):
                code += f"Set Arg{index}=\"{arg}\"\n"
            cmd = "\n%Exe%"
            for index in range(1, len(script.args) + 1):
                cmd += f"  %Arg{index}%"
            cmd += "  %*\n\n"
            code += cmd

    if script.after:
        for after in script.after:
            code += f"{after}\n"
        code += "\n"

    if script.commands:
        code += "\n"
        for command in script.commands:
            code = code + command + "\n\n"
        code += "\n"

    code += "EndLocal"

    with open(script.path, "w") as file:
        file.write(code)


def create_script_psl_file(script):
    code = ""

    if script.before:
        for before in script.before:
            code += f"{before}\n"
        code += "\n"

    if script.exe:
        code += f"$Exe = \"{script.exe}\"\n\n"
        if not script.args or len(script.args) == 0:
            code += f"&  $Exe  $Args"
        elif len(script.args) == 1:
            code += f"$Arg=\"{script.args[0]}\"\n\n"
            code += f"&  $Exe  $Arg"
        elif len(script.args) > 1:
            for index, arg in enumerate(script.args, start=1):
                code += f"$Arg{index}=\"{arg}\"\n"
            cmd = "\n&  $Exe"
            for index in range(1, len(script.args) + 1):
                cmd += f"  $Arg{index}   $Args"
            code += cmd

    if script.after:
        for after in script.after:
            code += f"{after}\n"
        code += "\n"

    if script.commands:
        code += "\n"
        for command in script.commands:
            code = code + command + "\n\n"
        code += "\n"

    with open(script.path, "w") as file:
        file.write(code)


def create_script():
    text = ""
    script: Script
    for script in scripts:
        if not script.exe and not script.commands:
            continue
        if script.type == "Bat":
            create_script_bat_file(script)
        if script.type == "PowerShell":
            create_script_psl_file(script)

        args = ' '.join(script.args) if script.args else ""
        text += f"{script.path.stem:>15}  {script.exe} {args} \n"

    text = text.rstrip()
    title = f"{path_script}\\"
    width = 120
    panel = Panel(text, title=title, title_align="center",
                  width=width, border_style="red")
    console.print(Align.center(panel))


def create_script_txt():
    text = "|  "

    each_length = 11  # 每个命令的长度
    total_cnt = 5  # 一行最多存在的命令数

    cnt = 0
    script: Script
    for script in scripts:
        if not script:
            continue
        name = script.path.stem
        if len(name) < each_length:
            if cnt >= total_cnt:
                text += "\n|  "
                cnt = 0
            text += name.ljust(each_length) + " "
            cnt += 1
        elif len(name) < each_length * 2:
            if cnt > total_cnt - 1:
                text += "\n|  "
                cnt = 1
            text += name.ljust(each_length * 2) + " "
            cnt += 2
        elif len(name) < each_length * 3:
            if cnt > total_cnt - 2:
                text += "\n|  "
                cnt = 1
            text += name.ljust(each_length * 3) + " "
            cnt += 3
        if cnt >= total_cnt:
            text += "  |"

    # 结尾空格补全 + |
    if cnt <= total_cnt:
        text += " " * (each_length + 1) * (total_cnt - cnt) + "  |"

    with open(path_script_txt, "w") as file:
        file.write(text)

    width = (each_length * total_cnt) + (total_cnt * 3)
    title = str(path_script_txt)
    panel = Panel(text, title=title, width=width,
                  title_align="center", border_style="red")
    console.print(Align.center(panel))

