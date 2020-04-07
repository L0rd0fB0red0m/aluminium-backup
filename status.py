from threading import Thread                                                    #for UI-Threading
import sys                                                                      #for closing the window
import time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
#for UI elements

from Restore.activity import Activity as restoreActivity
from Backup.activity import Activity as backupActivity


class showStatus(QWidget):
    """framework, either shows B or R progress"""

    def __init__(self, B_or_R, config):
        """Starts window and calls for start of activity
        Args: * B_or_R:bool -> True for Backup, false for Restore
              * config:dict -> configuration that is loaded in UI and is passed through to activity"""
        super().__init__()
        name = ["Restoring","Backing up"][B_or_R] #1 if true and 0 if false
        self.config = config
        #self.setFixedSize(1000,200)
        self.setWindowIcon(QIcon('.AlB/icon.ico'))
        self.setWindowTitle("AlB Running - " + name) #sets the title depending on whether B or R is displayed
        self.create_grid_layout()
        self.start_activity(B_or_R)


    def create_grid_layout(self):
        """puts every single widget into a grid, every widget must be mentionned in this func."""

        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.addWidget(self.progress_bar(), 0, 0, 1, 2)
        self.grid.addWidget(self.detail_progress(), 1, 0, 1, 2)
        self.grid.addWidget(self.elapsed(), 2, 0, 1, 2)
        self.grid.addWidget(self.button_stop(), 3, 0)
        self.grid.addWidget(self.button_pause(), 3, 1)

    def progress_bar(self):
        """shows progression as a percentage"""
        self.progression_bar = QProgressBar()
        self.progression_bar.setGeometry(200, 80, 250, 20)
        return self.progression_bar


    def detail_progress(self):
        """shows the path of the file that is being copied at the moment"""
        self.text_detail_progress = QTextEdit()
        self.text_detail_progress.setReadOnly(True)
        #white = QColor()
        #white.setRgb(255,255,255)
        #black = QColor()
        #black.setRgb(0,0,0)
        #self.text_detail_progress.setTextBackgroundColor(black)
        #self.text_detail_progress.setTextColor(white)

        self.text_detail_progress.insertPlainText("Starting... \n")
        return self.text_detail_progress


    def elapsed(self):
        """shows time elapsed since the start"""
        self.elapsed_time = QLabel("0:00")
        return self.elapsed_time


    def button_pause(self):
        """switches a bool in activity that interrupts the copying but can be resumed"""
        def button_action():
            self.activity.pause = not self.activity.pause
            if self.activity.pause:
                pause_button.setText("Resume")
            else:
                pause_button.setText("PAUSE")

        pause_button = QPushButton("PAUSE")
        pause_button.clicked.connect(button_action)
        return pause_button


    def button_stop(self):
        """stops everything: exits completely"""
        def stop_action():
            sys.exit(130)
            #130 is Exitcode for ctl-c, which is roughly what this is equivalent to
        self.stop_button = QPushButton("STOP")
        self.stop_button.clicked.connect(stop_action)
        return self.stop_button


    def update_progress_bar(self, percentage):
        """updates progression bar and copied file-message through a signal from activity
        Args: * percentage:int -> ratio between copied files and all files (gives an idea of the progression)"""
        self.progression_bar.setValue(100 * percentage)

    def update_detail_progress(self, detail_progress):
        """updates progression bar and copied file-message through a signal from activity
        Args: * detail_progress:str -> path+name of the file that is being copied"""
        self.text_detail_progress.insertPlainText(detail_progress + "\n")


    def update_elapsed(self,time_now):
        """updates elapsed time through a signal from activity
        Args: * elapsed_time:str-> datetime-timedelta between the launch and the emission of the signal"""
        elapsed_time = str(time_now - self.activity.start_time)[:-7]#.strftime("%H:%M:%S")
        self.elapsed_time.setText("Elapsed: " + elapsed_time)


    def finish_ui(self,unsuccesfull_log):
        """updates the UI once activity has finished, shows error messages
        Args: * unsuccesfull_log:list -> every file that threw a caught error during activity"""
        self.stop_button.setText("QUIT")
        self.progression_bar.setValue(100)
        self.text_detail_progress.insertPlainText("Finished \n")
        if len(self.activity.unsuccesfull_log) != 0:
            self.show_unsuccessfull(self.activity.unsuccesfull_log)


    def start_activity(self,B_or_R):
        """starts B or R process
        Args: * B_or_R:bool -> True for Backup and False for Restore"""
        if B_or_R:
            self.activity = backupActivity(self.config)
        else:
            self.activity = restoreActivity(self.config)
        self.activity.update_percentage.connect(self.update_progress_bar)
        self.activity.update_detail.connect(self.update_detail_progress)
        self.activity.elapsed.connect(self.update_elapsed)
        self.activity.finished.connect(self.finish_ui)
        self.activity.start()


    def show_message(self,text_to_show):
        """displays a message_box with a customizable message
        Args: * text_to_show:str -> text that will be displayed"""
        message_box = QMessageBox()
        message_box.setWindowTitle("Warning")
        message_box.setIcon(QMessageBox.Information)
        message_box.setText(text_to_show)
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec()


    def show_unsuccessfull(self,not_copied):
        """launches new-window displaying logged errors
        Args: * not_copied:list -> every file that threw a caught error during activity"""
        self.warningbox = warningBox(not_copied)
        self.warningbox.show()







class warningBox(QWidget):
    """Creates settings-window as a standalone entity"""
    def __init__(self,not_copied):
        """Sets up window
        Args: * not_copied:list -> every file that threw a caught error during activity"""
        super().__init__()
        self.setWindowIcon(QIcon('.AlB/icon.ico'))
        self.setWindowTitle("Warning")
        self.unsuccesfull_log = not_copied
        grid = QGridLayout()
        self.setLayout(grid)
        grid.addWidget(QLabel("Did not copy the following files:"),0,0)
        grid.addWidget(self.not_copied_list(),1,0)
        grid.addWidget(QLabel("Please carefully check that these aren't needed."),2,0)


    def not_copied_list(self):
        """QList for showing the missing files (scrollable)"""
        unsuccesfull_list = QListWidget()
        for i in self.unsuccesfull_log:
            unsuccesfull_list.addItem(QListWidgetItem(i))
        return unsuccesfull_list
