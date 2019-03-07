from threading import Thread
import time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
#for UI elements
from Restore import activity as RA
from Backup import activity as BA


class status_window(QWidget):
    """framework, either shows B or R progress"""
    def __init__(self,B_or_R,config):
        super().__init__()
        name = lambda B_or_R: "Backing up" if B_or_R else "Restoring"
        self.config = config
        self.resize(500,100)
        self.setWindowIcon(QIcon('icon.ico'))
        self.setWindowTitle("AlB Running - " + name(B_or_R)) #sets the title depending on whether B or R is displayed
        self.create_grid_layout()
        self.start_activity(B_or_R)


    def create_grid_layout(self):
        """puts every single widget into a grid, evry widget must be mentionned in this func."""
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.addWidget(self.progress_bar(), 0, 0, 1, 2)
        self.grid.addWidget(self.progress_list(), 1, 0, 1, 2)
        self.grid.addWidget(self.button_pause(), 3, 0)
        self.grid.addWidget(self.button_stop(), 3, 1)

    def progress_bar(self):
        self.progression_bar = QProgressBar()
        self.progression_bar.setGeometry(200, 80, 250, 20)
        return self.progression_bar

    def progress_list(self):
        self.progress_file_list = QListWidget()
        return self.progress_file_list


    def button_pause(self):
        def pause_action():
            self.activity.pause = True
            print("HEY")
            self.pause_button.setText("Resume")
            print("Might wanna add a resume button")
        self.pause_button = QPushButton("PAUSE")
        self.pause_button.clicked.connect(pause_action)
        return self.pause_button



    def button_stop(self):
        def stop_action():
            print("HEY")
        self.stop_button = QPushButton("STOP")
        self.stop_button.clicked.connect(stop_action)
        return self.stop_button




    def update_progress(self):
        time.sleep(1)
        most_recent_entry = ""
        while self.activity.progress != self.activity.max_progress:
            if self.activity.copied_files[-1] != most_recent_entry:
                print("ADDED STH")
                self.progress_file_list.addItem(QListWidgetItem(time.strftime("%H:%M:%S")+" - "+self.activity.copied_files[0]))#["TEST"]))#list element in here pls)
                self.progression_bar.setValue(100 * self.activity.progress / self.activity.max_progress)
                most_recent_entry = self.activity.copied_files[-1]


    def start_activity(self,B_or_R):
        self.UI_thread = Thread(target = self.update_progress)
        self.UI_thread.start()
        if B_or_R:
            self.activity = BA.activity(self.config)
        else:
            self.activity = RA.activity(self.config)

#Wanna hear a hilarious joke?
#This code is self explanatory
