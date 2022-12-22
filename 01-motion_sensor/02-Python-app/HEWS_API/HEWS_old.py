import sys
import time
import requests
from termcolor import colored, cprint
from playsound import playsound

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import *

sensor_url = "http://192.168.0.121/"
api_key = "impulse"

alarm_sound = "D:/Project/it_home_early_warning_system/01-motion_sensor/02-Python-app/HEWS_API/sound/sound1.mp3"
#alarm_sound = "/home/kijada/pyproject/hews/it_home_early_warning_system/01-motion_sensor/02-Python-app/HEWS_API/sound/sound1.mp3"

playsound(alarm_sound)

class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        self.mute = False
        self.alarm = False
        self.enable = False
        self.auto_reset = False
        self.time_counter = 0

        self.label_style = " color: white;"

        super(MainWindow, self).__init__()
        self.setStyleSheet("background-color: #EEEEEE;")
        self.setWindowTitle("Home Early Warning System")

        self.showMaximized()

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        self.set_button()

        self.box = QtWidgets.QLabel("")
        self.box.setAlignment(QtCore.Qt.AlignCenter)
        self.box.setFont(QFont('Arial', 40))
        self.box.setStyleSheet("background-color: #4c956c;" + self.label_style)
        self.layout.addWidget(self.box, 1, 0, 5, 20)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(250)
        self.timer.timeout.connect(self.update_window)
        self.timer.start()

    def set_button(self):
        button = QtWidgets.QPushButton("RESET")
        button.setStyleSheet("background-color: #AAAAAA;")
        button.clicked.connect(self.reset)
        self.layout.addWidget(button, 0, 0)

        button = QtWidgets.QCheckBox("START")
        button.toggled.connect(self.start)
        button.setChecked(True)
        self.layout.addWidget(button, 0, 1)

        button = QtWidgets.QCheckBox("Mute")
        button.toggled.connect(self.sound)
        self.layout.addWidget(button, 0, 2)

        button = QtWidgets.QCheckBox("AutoReset")
        button.toggled.connect(self.set_auto_reset)
        self.layout.addWidget(button, 0, 3)

    def update_window(self):
        self.time_counter += 1

        if self.enable:
            try:
                response = requests.get(sensor_url + api_key, timeout=0.25)
                response = response.json()

                message = "Event: " + str(response["state"]) + " \timpuls count: " + str(response["count"]) + " \t " + str(self.time_counter) + " \t " + str(self.alarm)
                sys.stdout.write("\r" + message)

                if (response["count"]):
                    cprint("\nMotion detected!\n", "red")
                    self.alarm = True
                    self.box.setStyleSheet("background-color: #d94430;" + self.label_style)
                    self.box.setText("ALARM !!!")
                    self.time_counter = 0

                    if not self.mute:
                        playsound(alarm_sound)
            except:
                message = "Connection timeout"
                sys.stdout.write("\r" + message)

        if self.auto_reset and self.alarm:
            if self.time_counter > 10:
                self.time_counter = 0
                self.reset()

        if self.alarm:
            if not self.mute:
                playsound(alarm_sound)
                print("alarm")

    def reset(self):
        print("\nRESET\n")
        self.alarm = False
        self.box.setStyleSheet("background-color: #4c956c;")
        self.box.setText("")

    def sound(self, state):
        if state:
            self.mute = True
        else:
            self.mute = False

    def start(self, state):
        if state:
            self.enable = True
        else:
            self.enable = False

    def set_auto_reset(self, state):
        self.time_counter = 0
        if state:
            self.auto_reset = True
        else:
            self.auto_reset = False



def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

main()