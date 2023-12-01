import os
import sys
import urllib.request
import zipfile, shutil
import io

import tkinter
from tkinter import ttk

import psutil
import threading

path = os.path.dirname(sys.executable)
zip_file = "template.zip"


def main_thread(pb_var: tkinter.DoubleVar):
    zip_file_ = download_url(file, zip_file, pb_var)
    check_app_is_stop()

    for item in os.listdir():
        print(item)
        if zip_file in item:
            continue

        if "Apply" in item:
            continue

        if os.path.isfile(item):
            os.remove(item)
        else:
            shutil.rmtree(item)

    zip_file_.extractall()
    bool_var.set(True)
    print("end")


def download_url(url, save_path, pb_var: tkinter.DoubleVar):
    resp = urllib.request.urlopen(url)
    length = resp.getheader('content-length')
    if length:
        length = int(length)
        blocksize = max(4096, length // 100)
    else:
        blocksize = 1000000  # just made something up

    print(length, blocksize)

    buf = io.BytesIO()
    size = 0
    while True:
        buf1 = resp.read(blocksize)
        if not buf1:
            break
        buf.write(buf1)
        size += len(buf1)
        if length:
            pb_var.set(size / length)

    return zipfile.ZipFile(buf)


def apply():
    file_ = zipfile.ZipFile(zip_file)
    file_.extractall()


def check_app_is_stop():
    is_run = False
    while not is_run:
        for process in psutil.process_iter():
            # TODO name process will is argv[2]
            if "MAOS" not in process.name():
                is_run = True


def quit_window(a, b, c):
    app.destroy()


if __name__ == '__main__':
    argv = sys.argv
    file = argv[1]
    print(file)
    app = tkinter.Tk()
    width = 300  # Width
    height = 90  # Height
    screen_width = app.winfo_screenwidth()  # Width of the screen
    screen_height = app.winfo_screenheight()  # Height of the screen

    # Calculate Starting X and Y coordinates for Window
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)

    app.geometry('%dx%d+%d+%d' % (width, height, x, y))
    app.title('updating...')
    app.resizable(False, False)

    bool_var = tkinter.BooleanVar(app, False)
    bool_var.trace_add("write", quit_window)

    pb_var = tkinter.DoubleVar(app, 0.0)
    pb = ttk.Progressbar(app, variable=pb_var, maximum=1)
    pb.place(relx=0.5, rely=0.5, relwidth=0.9, anchor="center")
    threading.Thread(target=main_thread, args=(pb_var,)).start()
    app.mainloop()


