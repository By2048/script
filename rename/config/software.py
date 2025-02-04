from functools import partial

from .base import version_x
from .base import capitalize
from .base import upper_1, upper_2, upper_3, upper_all

github = partial(version_x, match="GitHubDesktop", get="GitHub")
potplayer = partial(version_x, match="PotPlayer", get="PotPlayer")
ntlite = partial(version_x, match="NTLite", get="NTLite")  # noqa
postman = partial(version_x, match="Postman", get="Postman")
fdm = partial(version_x, match="FDM", get="FDM")
geek = partial(version_x, match="Geek", get="Geek")
firefox = partial(version_x, match="FireFox-Full", get="FireFox")
fsviewer = partial(version_x, match="FSViewer", get="FSViewer")
wechat = partial(version_x, match="WeChat", get="WeChat")
youdao = partial(version_x, match="YoudaoDict", get="YouDao")
wps = partial(version_x, match="WPS_Setup", get="WPS")

config_software = [

    github,
    potplayer,
    ntlite,
    postman,
    fdm,
    geek,
    fsviewer,
    wechat,
    youdao,
    wps,

    # Xftp-7.0.0063p.exe
    [r"(Xftp)(-)([\d\.]+)(\w)(.exe)", r"\1_\3\5"],

    # Xshell-7.0.0063p.exe
    [r"(Xshell)(-)([\d\.]+)(\w)(.exe)", r"\1_\3\5"],

    # THS_hevo_gc9.1.1.1.exe
    [r"(THS)(_hevo_gc)([\d\.]+)(.exe)", r"\1_\3\4"],

    # dotnet-sdk-8.0.203-win-x64.exe
    [r"(dotnet-sdk-)([\d\.]+)(-win-x64)(.exe)", r"DotNet_\2\4"],

    # ideaIU-2023.2.exe
    # pycharm-professional-2023.2.exe
    [r"(ideaIU)(-)([\d\.]+)(.exe)", r"IDEA_\3\4"],
    [r"(pycharm-professional)(-)([\d\.]+)(.exe)", r"PyCharm_\3\4"],

    # tportable-x64.4.10.2.zip
    [r"(tportable)(-x64.)([\d\.]+)(.zip)", r"Telegram_\3\4"],

    # aria2-1.36.0-win-64bit-build1.zip
    [r"(aria2)(-)([\d\.]+)(-win-64bit-build1)(.zip)", (r"\1_\3\5", capitalize)],

    # dexpot_1614_portable_r2439.zip
    [r"(dexpot)(_)([\d\.]+)(_portable)(\_\w+)(.zip)", (r"\1_\3\6", capitalize)],
    # dexpot_1614_r2439.exe
    [r"(dexpot)(_)([\d\.]+)(\_\w+)(.exe)", (r"\1_\3\5", capitalize)],

    # blender-4.0.1-windows-x64.msi
    [r"(blender)(-)([\d\.]+)(-windows-x64)(.msi)", (r"\1_\3\5", capitalize)],

    # ventoy-1.0.38-windows.zip
    [r"(ventoy)(-)([\d\.]+)(-windows)(.zip)", r"Ventoy_\3\5"],
    # iventoy-1.0.08-win64.zip
    [r"(iventoy)(-)([\d\.]+)(-win64)(.zip)", r"VentoyI_\3\5"],

    # BitComet_1.87_setup.exe
    [r"(BitComet)(_)([\d\.]+)(_setup)(.exe)", r"\1_\3\5"],

    # BCompare-zh-4.4.6.27483.exe
    [r"(BCompare)(-zh-)([\d\.]+)(.exe)", r"\1_\3\4"],

    # ffmpeg-2021-12-12-git-996b13fac4-full_build.7z
    [r"(ffmpeg)(-)([\d\-]+)(-)(git\-\w+)(\-full_build)(.7z)", (r"\1_\3\7", upper_2)],
    # ffmpeg-5.1.2-essentials_build.7z
    [r"(ffmpeg)(-)([\d\.]+)(-essentials_build)(.7z)", (r"\1_\3\5", upper_2)],

    # navicat150_premium_cs_x64.exe
    [r"(navicat)([\d]+)(_premium_cs_x64)(.exe)", (r"\1_\2\4", capitalize)],

    # cloudmusicsetup2.9.5.199424.exe
    [r"(cloudmusic)(setup)([\d\.]+)(.exe)", r"CloudMusic_\3\4"],

    # Clash.Nyanpasu_1.5.1_x64-setup.exe
    [r"(Clash)(.)(Nyanpasu)(_)([\d\.]+)(_x64-setup)(.exe)", r"\1\3\4\5\7"],

    # scrcpy-win64-v1.24.zip
    [r"(scrcpy)(-win64)(-v)([\d\.]+)(.zip)", r"Scrcpy_\4\5"],

    # mkvtoolnix-64-bit-79.0.7z
    [r"(mkvtoolnix)(-64-bit-)([\d\.]+)(.7z)", r"MKVToolNix_\3\4"],

    # rdm-2021.3.0.0.exe
    # resp-2022.3.0.0.exe
    [r"(rdm|resp)(-)([\d\.]+)(.exe)", (r"\1_\3\4", upper_all)],

    # QuiteRSS-0.19.4.zip
    [r"(QuiteRSS)(-)([\d\.]+)(.zip)", r"\1_\3\4"],

    # MobaXterm_Portable_v22.0.zip
    [r"(MobaXterm)(_Portable_)(v)([\d\.]+)(.zip)", r"\1_\4\5"],

    # FreeFileSync_11.8_Windows_Setup.exe
    [r"(FreeFileSync_)([\d\.]+)(_Windows_Setup)(.exe)", r"\1\2\4"],

    # TIM3.4.8.22092.exe
    [r"(TIM)([\d\.]+)(.exe)", r"\1_\2\3"],

    # SumatraPDF-3.3.3-64.zip  portable (zip) v
    [r"(SumatraPDF)(\-)([\d\.]+)(-64)(\.zip)", r"\1_\3_Portable\5"],
    # SumatraPDF-3.3.3-64-install.exe
    [r"(SumatraPDF)(\-)([\d\.]+)(-64)(-install)(\.exe)", r"\1_\3_Install\6"],

    # logioptionsplus_installer.exe
    [r"(logioptionsplus_installer.exe)", r"LogiOptionsPlus.exe"],

    # sysdiag-all-5.0.64.2-2021.11.3.1.exe
    [r"(sysdiag)(\-all\-)([\d\.]+)(\-)([\d\.]+)(.exe)", r"HuoRong_\3\6"],

    # Wireshark-win64-4.0.8.exe
    [r"(Wireshark)(-win64-)([\d\.]+)(.exe)", r"\1_\3\4"],
    # WiresharkPortable64_4.0.8.paf.exe
    [r"(Wireshark)(Portable)(64?)(_)([\d\.]+)(.paf)(.exe)", r"\1\2_\5\7"],

    # node-v14.17.0-win-x64.zip
    [r"(node)(-v)([\d\.]+)(-win-x64)(.zip)", (r"\1_\3\5", capitalize)],

    # DG5411178_x64.zip
    [r"(DG)(\d+)(_x64)(.zip)", r"DiskGenius_\2\4"],

    # GeForce_Experience_v3.27.0.112.exe
    [r"(GeForce)(_Experience_v)([\d\.]+)(.exe)", r"\1_\3\4"],

    # Everything-1.4.1.1005.x64.zip
    [r"(Everything)(-)([\d\.]+)(.x64)(.zip)", r"\1_\3\5"],
    # Everything-1.4.1.1005.x64-Setup.exe
    [r"(Everything)(-)([\d\.]+)(.x64-Setup)(.exe)", r"\1_\3\5"],

    # ScreenToGif.2.27.3.Setup.msi
    [r"(ScreenToGif)(\.)([\d\.]+)(.Setup)(.msi)", r"\1_\3\5"],
    # ScreenToGif.2.27.3.Portable.zip
    [r"(ScreenToGif)(\.)([\d\.]+)(.Portable|.Portable.x64)(.zip)", r"\1_\3\5"],

    # Git-2.31.0-64-bit.exe
    [r"(Git)(-)([\d\.]+)(-64-bit)(.exe)", r"\1_\3\5"],
    # PortableGit-2.31.0-64-bit.7z.exe
    [r"(Portable)(Git)(-)([\d\.]+)(-64-bit)(.7z)(.exe)", r"\2_\4\6\7"],

    # platform-tools_r33.0.3-windows.zip
    [r"(platform-tools)(_r)([\d\.]+)(-windows)(.zip)", r"AndroidTools_\3\5"],

    # Q-Dir_Portable_x64.zip
    [r"(Q-Dir)(_)(Portable_x64)(.zip)", r"\1\4"],
    # Q-Dir_Portable_x64_9.97.zip
    [r"(Q-Dir)(_)(Portable_x64)(_)([\d\.]+)(.zip)", r"\1\2\5\6"],
    # Q-Dir_x64.exe
    [r"(Q-Dir)(_)(x64)(.exe)", r"\1\4"],

    # calibre-portable-installer-5.32.0.exe
    [r"(calibre)(-portable-installer-)([\d\.]+)(.exe)", (r"\1_\3\4", capitalize)],

    # VSCodeSetup-x64-1.61.2.exe
    [r"(VSCode)(Setup)(-x64-)([\d\.]+)(.exe)", r"\1_\4\5"],

    # AutoHotkey_1.1.33.10_setup.exe
    [r"(AutoHotkey)(_)([\d\.]+)(_setup)(.exe)", r"\1_\3\5"],
    # AutoHotkey_2.0-beta.3.zip
    [r"(AutoHotkey)(_)([\d\.]+)(-beta)([\d\.]+)(.zip)", r"\1_\3\5\6"],

    # Maye.1.2.6-20211001.zip
    [r"(Maye)(.)(\d.\d.\d)(-)(\d+)(.zip)", r"\1_\3\6"],

    # VeraCrypt_1.24-Update7.zip
    [r"(VeraCrypt)(_)([\d\.]+)(-Update)(\d)(.zip)", r"\1\2\3.\5\6"],
    # VeraCrypt Setup 1.24-Update7
    [r"(VeraCrypt)( Setup )([\d\.]+)(-Update)(\d)(.exe)", r"\1_\3.\5\6"],

    # go1.17.3.windows-arm64.zip
    [r"(go)([\d\.]+)(.windows)(-amd64|-arm64)(.zip)", (r"\1_\2\5", capitalize)],

    # jdk-17_windows-x64_bin.zip
    [r"(jdk)(-)([\d\.]+)(_windows)(-x64_bin)(.zip)", (r"\1_\3\6", upper_all)],

    # frp_0.38.0_windows_amd64.zip
    [r"(frp)(_)([\d\.]+)(_windows_amd64)(.zip)", (r"\1_\3\5", capitalize)],

    # Shadowsocks-4.4.0.185.zip
    [r"(Shadowsocks)(-)([\d\.]+)(.zip)", r"\1_\3\4"],

    # VMware-workstation-full-16.1.0-17198959.exe
    [r"(VMware)(-workstation-full-)([\d\.]+)(-)(\d+)(.exe)", r"\1_\3.\5\6"],

    # VirtualBox-6.1.28-147628-Win.exe
    [r"(VirtualBox)(-)([\d\.]+)(-)(\d+)(-Win)(.exe)", r"\1_\3.\5\7"],
    # Oracle_VM_VirtualBox_Extension_Pack-6.1.28.vbox-extpack
    [r"(Oracle_VM_)(VirtualBox)(_Extension_Pack)(-)([\d\.]+)(.vbox-extpack)", r"\2_\5\6"],

    # Sandboxie-Plus-x64-v0.9.6.exe
    [r"(Sandboxie)(-Plus)(-x64)(-v)([\d\.]+)(.exe)", r"\1_\5\6"],

    # blender-4.0.2-windows-x64.zip
    [r"(blender-)([\d\.]+)(-windows-x64)(.zip)", r"Blender_\2\4"],

    # Anaconda3-2023.09-0-Windows-x86_64.exe
    [r"(Anaconda3-)([\d\.]+)(-0-Windows-x86_64)(.exe)", r"Anaconda_\2\4"],

    # XMind-for-Windows-64bit-11.1.1-202110191919.exe
    # Xmind-for-Windows-x64bit-22.11.3656.exe
    [r"(XMind|Xmind)(-for)(-Windows-)(64bit|x64bit)(-)([\d\.]+)(.exe)", r"\1_\6\7"],

    # VSCode-win32-x64-1.75.1.zip
    # VSCodeSetup-x64-1.75.1.exe
    [r"(VSCode)(-win32-x64-)([\d\.]+)(.zip)", r"\1_\3\4"],
    [r"(VSCode)(Setup)(-x64-)([\d\.]+)(.exe)", r"\1_\4\5"],

    # FoxmailSetup_7.2.20.273.exe
    [r"(Foxmail)(Setup)(_)([\d\.]+)(.exe)", r"\1\3\4\5"],

    # MouseInc2.12.1.7z
    [r"(MouseInc)([\d\.]+)(.7z)", r"\1_\2\3"],

    # npp.8.1.9.portable.x64.zip
    [r"(npp.)([\d\.]+)(.portable)(.x64)(.zip)", r"Notepad++_\2\5"],

    # QuickLook-3.7.0.zip
    [r"(QuickLook)(-)([\d\.]+)(.zip)", r"\1_\3\4"],

    # Apifox-2.1.34.exe
    [r"(Apifox)(-)([\d\.]+)(.exe)", r"\1_\3\4"],

    # Firefox Setup 94.0.1.exe
    [r"(Firefox)(\s)(Setup)(\s)([\d\.]+)(.exe)", r"\1_\5\6"],
    firefox,

    # Snipaste-2.6.6-Beta-x64.zip
    [r"(Snipaste)(-)([\d\.]+)(-Beta-x64)(.zip)", r"\1_\3\5"],

    # Obsidian.0.13.19.exe
    [r"(Obsidian)(\.)([\d\.]+)(\.exe)", r"\1_\3\4"],

    # jetbrains-toolbox-1.22.10685.exe
    [r"(jetbrains)(-)(toolbox)(-)([\d\.]+)(.exe)", (r"\1_\5\6", capitalize)],

    # Samsung_Magician_Installer_Official_7.0.0.510.zip
    [r"(Samsung_)(Magician)(_Installer)(_Official)(_)([\d\.]+)(.zip)", r"\2\5\6\7"],

    # zeal-portable-0.6.1-windows-x64.zip
    [r"(zeal)(-portable)(-)([\d\.]+)(-windows-x64)(.zip)", (r"\1_\4\6", capitalize)],

    # Postman-win64-9.5.0-Setup.exe
    [r"(Postman)(-win64-)([\d\.]+)(-Setup)(.exe)", r"\1_\3\5"],

    # qbittorrent_4.4.1_x64_setup.exe
    [r"(qbittorrent)(_)([\d\.]+)(_x64_setup)(.exe)", r"QBittorrent_\3\5"],

    # chrome-win.zip
    [r"(chrome)(-)(win)(.zip)", r"Chromium.zip"],
    # chromedriver_win32.zip
    [r"(chromedriver)(_)(win32)(.zip)", r"ChromeDriver.zip"],

    # PowerShell-7.2.2-win-x64.zip
    [r"(PowerShell)(-)([\d\.]+)(-win-x64)(.zip)", r"\1_\3\5"],

    # gvim_8.2.2825_x86_signed.exe
    [r"(gvim)(_)([\d\.]+)(_x86_signed)(.exe)", r"GVim_\3\5"],

    # PowerToysSetup-0.36.0-x64.exe
    [r"(PowerToys)(Setup-)([\d\.]+)(-x64)(.exe)", r"\1_\3\5"],

    # WindTerm_2.5.0_Windows_Portable_x86_64.zip
    [r"(WindTerm_)([\d\.]+)(_Windows_Portable_x86_64)(.zip)", r"\1\2\4"],

    # OBS-Studio-29.0.1.zip
    # OBS-Studio-29.0.1-Full-Installer-x64.exe
    [r"(OBS)(-Studio-)([\d\.]+)(.zip)", r"\1_\3\4"],
    [r"(OBS)(-Studio-)([\d\.]+)(-Full-Installer-x64)(.exe)", r"\1_\3\5"],

    # LibreOffice_7.4.5_Win_x64.msi
    [r"(LibreOffice)(_)([\d\.]+)(_Win_x64)(.msi)", r"\1_\3\5"],
    # LibreOffice_7.4.5_Win_x64_sdk.msi
    [r"(LibreOffice)(_)([\d\.]+)(_Win_x64)(_sdk)(.msi)", r"\1SDK_\3\6"],

]