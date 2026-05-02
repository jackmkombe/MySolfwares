import sys
from cx_Freeze import setup, Executable

import customtkinter
import os

ctk_path = os.path.dirname(customtkinter.__file__)

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "sys", "requests", "bs4", "docx", "reportlab", "customtkinter", "tkinter", "threading", "re", "time", "random", "deep_translator"],
    "includes": ["scraper", "app"],
    "include_files": [(ctk_path, "lib/customtkinter")],
    "excludes": ["matplotlib", "numpy", "scipy", "PIL"],
}

# base="Win64GUI" should be used for GUI apps
base = None
if sys.platform == "win64":
    base = "Win64GUI"

# Desktop and Menu shortcuts
shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "FetchNovel",             # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]FetchNovel.exe",# Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     ),
    ("StartMenuShortcut",      # Shortcut
     "ProgramMenuFolder",      # Directory_
     "FetchNovel",             # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]FetchNovel.exe",# Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     ),
]

msi_data = {"Shortcut": shortcut_table}

# MSI UI and installation options
bdist_msi_options = {
    "upgrade_code": "{98765432-1234-5678-9012-ABCDEF123456}",
    "add_to_path": True,
    "initial_target_dir": r"[ProgramFiles64Folder]\FetchNovel",
    "all_users": True,
    "data": msi_data,
}

setup(
    name="FetchNovel",
    version="1.0",
    author="FetchNovel Studio",
    description="FetchNovel - Modern Novel Scraper for Windows 11",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options
    },
    executables=[
        Executable(
            "run.py", 
            base=base, 
            target_name="FetchNovel.exe",
            icon=None # You can provide path to a .ico here for a clean look
        )
    ],
)
