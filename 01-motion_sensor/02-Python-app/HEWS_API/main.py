import sys
import os
import time
from datetime import datetime

import signal
import requests
from playsound import playsound

from threading import Thread, Event

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import *

sensor_url = "http://192.168.0.121/"
api_key = "impulse"

sound_dir = "sound"

class ApiHandling(Thread):
    print("API Thread Run...")

    def run(self):
        print("run api")

    def api_get(self):
        print("api get")

class SoundHandling(Thread):
    print("Sound Thread Run...")
    sound_lib_dir = ""
    sound_lib = []
    play_loop = False
    loop_sound = 0
    loop_period = 5

    def run(self):
        print("sound init")
        self.get_sound_lib_path()
        self.get_sound_list()

        time_now = datetime.now()
        previous_time = time_now

        self.play_loop = True

        while(True):
            time_now = datetime.now()

            if (time_now - previous_time).total_seconds() > self.loop_period:
                print("Time loop")
                if self.play_loop:
                    self.play_sound(self.loop_sound)
                previous_time = datetime.now()


    def get_sound_lib_path(self):
        self.sound_lib_dir = os.getcwd()
        self.sound_lib_dir = os.path.join(self.sound_lib_dir, sound_dir)
        print("Sound lib dir:", self.sound_lib_dir)

    def get_sound_list(self):
        raw_sound_lib = os.listdir(self.sound_lib_dir)
        print(raw_sound_lib)
        for sound in raw_sound_lib:
            try:
                sound_dir = os.path.join(self.sound_lib_dir, sound)
                sound_name = sound[0:sound.index(".")]
                SoundHandling.sound_lib.append([sound_name, sound_dir])
            except:
                print("Error sound lib, file:", sound)

        print("Sound lib: ", self.sound_lib)

    def play_sound(self, index):
        playsound(self.sound_lib[index][1])


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        print("Main Thread Run")

        self.time_counter = 0

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
    sound_thread = SoundHandling()
    sound_thread.start()
    api_thread = ApiHandling()
    api_thread.start()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
    exit()

main()