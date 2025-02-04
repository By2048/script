config_iso = [

    # manjaro-xfce-21.1.6-211017-linux513.iso
    [r"(manjaro)(-)(\w+)(-)([\d\.]+)(-)(\d+)(-linux)(\d+)(.iso)",
     r"Manjaro [version]\5 [linux]\9 [data]\7 [type]\3\10"],

    # debian-11.5.0-amd64-DVD-1.iso
    [r"(debian)(-)([\d\.]+)(-amd64-DVD-1)(.iso)", r"Debian_\3\5"],

    # debian-11.5.0-amd64-netinst.iso
    [r"(debian)(-)([\d\.]+)(-amd64-)(netinst)(.iso)", r"Debian_\3_NetInstall\6"],

    # ubuntu-18.04.6-live-server-amd64.iso
    [r"(ubuntu)(-)([\d\.]+)(-live-server-amd64)(.iso)", r"Ubuntu_Server_\3\5"],
    # ubuntu-22.04.2-desktop-amd64.iso
    [r"(ubuntu)(-)([\d\.]+)(-desktop-amd64)(.iso)", r"Ubuntu_Desktop_\3\5"],

    # deepin-desktop-community-20.8-amd64.iso
    # deepin-desktop-community-23-Alpha2-amd64.iso
    [r"(deepin)(-desktop-community-)([\d\.]+)(-amd64)(.iso)", r"Deepin_\3\5"],
    [r"(deepin)(-desktop-community-)(\d+)(-Alpha)(\d)(-amd64)(.iso)",
     r"Deepin_Alpha_\3.\5\7"],

    # kali-linux-2023.1-installer-amd64.iso
    # kali-linux-2023.1-vmware-amd64.7z
    [r"(kali)(-linux-)([\d\.]+)(-installer-amd64)(.iso)", r"Kali_\3\5"],
    [r"(kali)(-linux-)([\d\.]+)(-vmware-amd64)(.7z)", r"Kali_\3\5"],

]