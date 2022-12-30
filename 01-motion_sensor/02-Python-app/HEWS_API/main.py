import sys
import os
import time
from datetime import datetime

import signal
import requests
from playsound import playsound

from threading import Thread

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import *

sensors_set = ["192.168.0.121", "192.168.0.122", "192.168.0.123"]

class ApiTask:
    api_key = "impulse"

    def __init__(self, sensors_set):
        print("API Thread Run...")
        self.dada_ready = False
        self.warning = []
        self.alarm = []
        self.ip_set = []

        self.init_signals(sensors_set)

    def init_signals(self, sensors_set):
        print("Init sensors api, ", sensors_set)
        for sensor in sensors_set:
            self.ip_set.append(sensor)
            self.warning.append(False)
            self.alarm.append(False)

    def update_data_async(self):
        #print("Async",  end="")
        update = Thread(target=self.update_data, daemon=True)
        update.start()

    def update_data(self):
        #print("Updating data")
        self.dada_ready = False

        for i in range(len(self.ip_set)):
            try:
                sensor_url = "http://" + self.ip_set[i] + "/" + ApiTask.api_key
                response = requests.get(sensor_url, timeout=0.300).json()

                if response["count"] > 0:
                    print("Alarm:", self.ip_set[i])
                    self.alarm[i] = True

                self.warning[i] = False

            except Exception as error:
                #print("warning:", self.ip_set[i], error)
                self.warning[i] = True
                update_with_timeout = Thread(target=self.update_data_with_timeout, args=(i, 10,), daemon=True)
                update_with_timeout.start()

        self.dada_ready = True

    def update_data_with_timeout(self, index, timeout=10):
        try:
            sensor_url = "http://" + self.ip_set[index] + "/" + ApiTask.api_key
            response = requests.get(sensor_url, timeout=timeout).json()

            if response["count"] > 0:
                print("Alarm:", self.ip_set[index])
                self.alarm[index] = True

            self.warning[index] = False

        except Exception as error:
            # print("warning:", self.ip_set[i], error)
            self.warning[index] = True

class SoundTask:
    def __init__(self):
        print("Sound Thread Run...")
        self.sound_lib_dir = ""
        self.sound_lib = []
        self.sound_lib_full = []
        self.mute = False

        self.alarm_sound = 0
        self.warning_sound = 1
        self.tick_sound = 4

        self.init_sound_lib_path()
        self.init_sound_list()
        self.show_sound_lib()

    def init_sound_lib_path(self):
        self.sound_lib_dir = os.getcwd()
        self.sound_lib_dir = os.path.join(self.sound_lib_dir, "sound")
        print("Sound lib dir:", self.sound_lib_dir)

    def init_sound_list(self):
        raw_sound_lib = os.listdir(self.sound_lib_dir)
        #print(raw_sound_lib)
        for sound in raw_sound_lib:
            try:
                sound_dir = os.path.join(self.sound_lib_dir, sound)
                sound_name = sound.split(".")
                if sound_name[1] == "wav":
                    self.sound_lib.append(sound_name[0])
                    self.sound_lib_full.append(sound_dir)

            except:
                print("Error sound lib, file:", sound)

        #print("Sound lib: ", self.sound_lib)

    def show_sound_lib(self):
        print("\nSOUND LIB:\n--------------------")
        for i in range(len(self.sound_lib)):
            print(i, " \t->\t ", self.sound_lib[i])
        print("----------\n")

    def play_sound(self, index):
        if not self.mute:
            sound = self.sound_lib_full[index]
            play = Thread(target=playsound, args=(sound,), daemon=True)
            play.start()

    def alarm(self):
        self.play_sound(self.alarm_sound)

    def waring(self):
        self.play_sound(self.warning_sound)

    def tick(self):
        self.play_sound(self.tick_sound)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        print("Window run...")

        self.time_counter = 0
        self.tick_counter = 0
        self.reset_counter = 0

        self.auto_reset = False
        self.reset_counter_flag = False
        self.enabled = False
        self.reset_flag = False

        self.white_text = "color: #FFFFFF; "
        self.black_text = "color: #000000; "
        self.red_background = "background-color: #DA3D40; "
        self.green_background = "background-color: #3BA55C; "
        self.yellow_background = "background-color: #FED811; "
        self.active_background = "background-color: #999999; "
        self.inactive_background = "background-color: #DDDDDD; "

        self.play_sound = SoundTask()
        self.play_sound.mute = True

        self.api = ApiTask(sensors_set)
        # self.api.update_data_async()

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.setup_gui()

        print("Timer setup... ", end="")
        self.timer = QtCore.QTimer()
        self.timer.setInterval(250)
        self.timer.timeout.connect(self.main_loop)
        self.timer.start()
        print("done!")

    def main_loop(self):
        self.time_counter += 1
        self.tick_counter += 1
        self.reset_counter += 1
        #print("Running", self.time_counter, self.api.dada_ready)

        if self.tick_counter > 4:
            self.tick_counter = 0
            if self.enabled:
                self.play_sound.tick()

        #print("Reset timer: ", self.reset_counter, self.reset_counter_flag)
        if self.reset_counter > 25:
            self.reset_counter = 0
            self.reset_counter_flag = False
            if self.auto_reset:
                self.reset_flag = True

        if self.reset_flag:
            if self.api.dada_ready:
                self.reset_api_status()
            self.update_window()

        if self.api.dada_ready:
            self.api.dada_ready = False
            self.update_window()
            if self.enabled:
                self.api.update_data_async()
            print(".", end="")


    def update_window(self):
        alarm_flag = False
        warning_flag = False

        for i in range(len(self.box_set)):
            if self.api.alarm[i]:
                self.box_set[i].setStyleSheet(self.red_background + self.white_text)
                self.box_set[i].setText("ALARM !!!\n" + self.api.ip_set[i])
                alarm_flag = True
            elif self.api.warning[i]:
                self.box_set[i].setStyleSheet(self.yellow_background + self.white_text)
                self.box_set[i].setText("WARNING\n" + self.api.ip_set[i])
                warning_flag = True
            else:
                self.box_set[i].setStyleSheet(self.green_background + self.white_text)
                self.box_set[i].setText(self.api.ip_set[i])

        if alarm_flag:
            self.main_box.setStyleSheet(self.red_background + self.white_text)
            self.main_box.setText("ALARM !!!")
            self.play_sound.alarm()
            if not self.reset_counter_flag:
                self.reset_counter = 0
                self.reset_counter_flag = True
        else:
            self.main_box.setStyleSheet(self.green_background + self.white_text)
            self.main_box.setText(" ")
            self.reset_counter_flag = False

        # if warning_flag:
        #     self.play_sound.waring()

    def reset_api_status(self):
        for i in range(len(self.api.alarm)):
            self.api.alarm[i] = False
            #self.api.warning[i] = False

        self.reset_flag = False

    def setup_gui(self):
        print("Setting up GUI... ")

        self.setStyleSheet("background-color: #EEEEEE;")
        self.setWindowTitle("Home Early Warning System")

        self.box_set = []
        for i in range(len(sensors_set)):
            box = QtWidgets.QLabel("")
            box.setAlignment(QtCore.Qt.AlignCenter)
            box.setFont(QFont('Arial', 16))
            box.setStyleSheet(self.yellow_background + self.white_text)
            self.layout.addWidget(box, (1+(25*i)), 0, 25, 5)
            self.box_set.append(box)

        self.main_box = QtWidgets.QLabel("")
        self.main_box.setAlignment(QtCore.Qt.AlignCenter)
        self.main_box.setFont(QFont('Arial', 32))
        self.main_box.setStyleSheet(self.yellow_background + self.white_text)
        self.layout.addWidget(self.main_box, 1, 5, len(sensors_set)*25, 25)

        self.button_start = QtWidgets.QPushButton("START")
        self.button_start.setStyleSheet(self.inactive_background)
        self.button_start.clicked.connect(self.start)
        self.layout.addWidget(self.button_start, 0, 0, 1, 1)

        button = QtWidgets.QPushButton("RESET")
        button.setStyleSheet(self.inactive_background)
        button.setStyleSheet(self.inactive_background)
        button.clicked.connect(self.reset)
        self.layout.addWidget(button, 0, 4, 1, 1)

        self.button_auto_reset = QtWidgets.QPushButton("AutoReset")
        self.button_auto_reset.setStyleSheet(self.inactive_background)
        self.button_auto_reset.clicked.connect(self.set_auto_reset)
        self.layout.addWidget(self.button_auto_reset, 0, 1, 1, 1)

        self.button_mute = QtWidgets.QPushButton("Mute")
        self.button_mute.setStyleSheet(self.active_background)
        self.button_mute.clicked.connect(self.set_mute)
        self.layout.addWidget(self.button_mute, 0, 2, 1, 1)

        self.button_settings = QtWidgets.QPushButton("Settings")
        self.button_settings.setStyleSheet(self.inactive_background)
        self.button_settings.clicked.connect(self.settings_action)
        self.layout.addWidget(self.button_settings, 0, 29, 1, 1)

    def reset(self):
        print("Reset")
        self.reset_flag = True

    def start(self):
        if self.enabled:
            self.enabled = False
            self.button_start.setStyleSheet(self.inactive_background)
            self.reset_flag = True
        else:
            self.api.update_data_async()
            self.enabled = True
            self.button_start.setStyleSheet(self.active_background)
        print("Start: ", self.enabled)

    def set_mute(self):
        if self.play_sound.mute:
            self.play_sound.mute = False
            self.button_mute.setStyleSheet(self.inactive_background)
        else:
            self.play_sound.mute = True
            self.button_mute.setStyleSheet(self.active_background)
        print("Mute: ", self.play_sound.mute)

    def set_auto_reset(self):
        if self.auto_reset:
            self.auto_reset = False
            self.button_auto_reset.setStyleSheet(self.inactive_background)
        else:
            self.auto_reset = True
            self.button_auto_reset.setStyleSheet(self.active_background)
        print("Auto reset: ", self.auto_reset)

    def settings_action(self):
        print("Show settings")
        try:
            dialog = settings_window(self.play_sound.sound_lib)
            dialog.response.connect(self.set_settings)
            dialog.exec()
        except Exception as error:
            print(error)

    def set_settings(self, alarm_s, warning_s, tick_s):
        print("Set settings...")
        if alarm_s != -1:
            self.play_sound.alarm_sound = alarm_s

        if warning_s != -1:
            self.play_sound.warning_sound = warning_s

        if tick_s != -1:
            self.play_sound.tick_sound = tick_s


class settings_window(QtWidgets.QDialog):
    response = QtCore.pyqtSignal(int, int, int)

    def __init__(self, sound_lib):
        super().__init__()
        #print("Setting window init...")

        self.sound_list = sound_lib

        self.sound_alarm = -1
        self.sound_warning = -1
        self.sound_tick = -1


        self.active_background = "background-color: #999999; "
        self.inactive_background = "background-color: #DDDDDD; "

        self.setWindowTitle("Settings")

        self.layout_dialog = QtWidgets.QGridLayout()
        self.setLayout(self.layout_dialog)
        self.setup_dialog_gui()

    def setup_dialog_gui(self):
        #print("Settings up dialog GUI...")

        self.button_submit = QtWidgets.QPushButton("Submit")
        self.button_submit.setStyleSheet(self.inactive_background)
        self.button_submit.clicked.connect(self.submit_action)
        self.layout_dialog.addWidget(self.button_submit, 4, 0, 1, 1)

        label = QtWidgets.QLabel("Alarm sound:")
        self.layout_dialog.addWidget(label, 0, 0, 1, 1)

        self.sound_select_alarm = QtWidgets.QComboBox()
        self.sound_select_alarm.addItems(self.sound_list)
        self.sound_select_alarm.activated.connect(self.set_alarm_sound)
        self.layout_dialog.addWidget(self.sound_select_alarm, 0, 1, 1, 1)

        label = QtWidgets.QLabel("Warning sound:")
        self.layout_dialog.addWidget(label, 1, 0, 1, 1)

        self.sound_select_warning = QtWidgets.QComboBox()
        self.sound_select_warning.addItems(self.sound_list)
        self.sound_select_warning.activated.connect(self.set_warning_sound)
        self.layout_dialog.addWidget(self.sound_select_warning, 1, 1, 1, 1)

        label = QtWidgets.QLabel("Tick sound:")
        self.layout_dialog.addWidget(label, 2, 0, 1, 1)

        self.sound_select_tick = QtWidgets.QComboBox()
        self.sound_select_tick.addItems(self.sound_list)
        self.sound_select_tick.activated.connect(self.set_tick_sound)
        self.layout_dialog.addWidget(self.sound_select_tick, 2, 1, 1, 1)

    def submit_action(self):
        print("Submit settings...")
        self.response.emit(self.sound_alarm, self.sound_warning, self.sound_tick)
        self.close()

    def set_alarm_sound(self, index):
        self.sound_alarm = index

    def set_warning_sound(self, index):
        self.sound_warning = index

    def set_tick_sound(self, index):
        self.sound_tick = index


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

main()
