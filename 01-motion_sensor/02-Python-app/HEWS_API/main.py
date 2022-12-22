import sys
import os
import time

import signal
import requests
from termcolor import colored, cprint
from playsound import playsound

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import *

sensor_url = "http://192.168.0.121/"
api_key = "impulse"

sound_file_dir = "sound"

class ApiHandling(QObject):
    print("API Thread Run...")

    def api_get(self):
        print("api get")

class SoundHandling(QObject):
    print("Sound Thread Run...")
    sound_lib = []

    def get_sound_list(self):
        current_dir = os.getcwd()
        print(current_dir)
        sound_lib_path = os.path.join(current_dir, sound_file_dir)
        print(sound_lib_path)
        raw_sound_lib = os.listdir(sound_lib_path)

        for s in range(len(raw_sound_lib)):
            sound_path = os.path.join(sound_lib_path, raw_sound_lib[s])
            SoundHandling.sound_lib.append([s, sound_path])

        for sound in SoundHandling.sound_lib:
            print(sound[1])
            playsound(sound[1])


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        print("Main Thread Run")

        self.time_counter = 0

        self.thread = QThread()
        self.api_thread = ApiHandling()
        self.api_thread.moveToThread(self.thread)
        self.soud_thread = SoundHandling();
        self.soud_thread.moveToThread(self.thread)
        self.thread.start()
        print("Thread running...")

        self.soud_thread.get_sound_list()

        print("Timer setup... ", end="")
        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_window)
        self.timer.start()
        print("done!")

    def update_window(self):
        self.time_counter += 1
        print("Running", self.time_counter)

def exit_task(app):
    print("Exit")

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

main()