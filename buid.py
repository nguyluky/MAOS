import shutil
import time

import PyInstaller.__main__
import os
import customtkinter

path = os.path.dirname(__file__)
ctk_path = os.path.dirname(customtkinter.__file__)

# pyinstaller --noconfirm --onedir --windowed --add-data "d:/code/setting_app/venv3.9/lib/site-packages/customtkinter;customtkinter/" --add-data "D:\code\setting_app\ValLib;ValLib"  "D:\code\setting_app\main.py"
PyInstaller.__main__.run([
    "--noconfirm",
    '--onedir',
    "--windowed",
    '--add-data', fr"{ctk_path};customtkinter/",
    "--add-data", fr"{path}\ValLib;ValLib",

    "--add-data", fr"{path}\assets;assets",

    "--workpath", fr"{path}\.buid\buid",
    "--distpath", fr"{path}\.buid",
    "--icon", fr"{path}\assets\icons\icon.ico",
    "--name", "MAOS",
    fr"{path}\MAOS.py"
])

PyInstaller.__main__.run([
    '--onefile',
    "--windowed",
    "--workpath", fr"{path}\.buid\buid",
    "--distpath", fr"{path}\.buid",
    "--name", "ApplyUpdate",
    fr"{path}\ApplyUpdate.py"
])
time.sleep(5)

shutil.move(f"{path}\.buid\ApplyUpdate.exe", f"{path}\.buid\MAOS\ApplyUpdate.exe")
