from threading import Thread                                                    #for UI-Threading
import sys                                                                      #for closing the window

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
#for UI elements

from Restore.activity import Activity as RestoreActivity
from Backup.activity import Activity as BackupActivity


class status_window(QWidget):
    """framework, either shows B or R progress"""
    def __init__(self,B_or_R,config):
        super().__init__()
        name = lambda B_or_R: "Backing up" if B_or_R else "Restoring"
        self.running = True
        self.config = config
        self.resize(500,100)
        self.setWindowIcon(QIcon('icon.ico'))
        self.setWindowTitle("AlB Running - " + name(B_or_R)) #sets the title depending on whether B or R is displayed
        self.create_grid_layout()
        self.start_activity(B_or_R)


    def create_grid_layout(self):
        """puts every single widget into a grid, every widget must be mentionned in this func."""
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.addWidget(self.progress_bar(), 0, 0, 1, 2)
        self.grid.addWidget(self.now_copying(), 1, 0, 1, 2)
        self.grid.addWidget(self.elapsed(), 2, 0, 1, 2)
        self.grid.addWidget(self.button_stop(), 3, 0)
        self.grid.addWidget(self.button_pause(), 3, 1)


    def progress_bar(self):
        """shows progression as a percentage"""
        self.progression_bar = QProgressBar()
        self.progression_bar.setGeometry(200, 80, 250, 20)
        return self.progression_bar


    def now_copying(self):
        """shows the path of the file that is being copied at the moment"""
        self.label_now_copying = QLabel()
        return self.label_now_copying


    def elapsed(self):
        """Shows time elapsed since the start"""
        self.elapsed_time = QLabel()
        return self.elapsed_time


    def button_pause(self):
        """switches a bool in activity that interrupts the copying but can be resumed"""
        def button_action():
            self.activity.pause = not self.activity.pause
            if self.activity.pause:
                self.pause_button.setText("Resume")
            else:
                self.pause_button.setText("PAUSE")

        self.pause_button = QPushButton("PAUSE")
        self.pause_button.clicked.connect(button_action)
        return self.pause_button


    def button_stop(self):
        """stops everything: exits completely"""
        def stop_action():
            sys.exit(130)
            #130 is Exitcode for ctl-c, which is roughly what this is equivalent to
        self.stop_button = QPushButton("STOP")
        self.stop_button.clicked.connect(stop_action)
        return self.stop_button


    def update_progress(self, percentage, now_copying):
        """updates UI ie. progression bar and copied file-message. Creates QUIT button after being finished"""
        self.progression_bar.setValue(100 * percentage)
        self.label_now_copying.setText("Copying: " + now_copying)

    def update_elapsed(self,elapsed_time):
        self.elapsed_time.setText("Elapsed: "+elapsed_time)


    def finish_ui(self,unsuccesfull_log):
        self.running = False
        self.stop_button.setText("QUIT")
        self.label_now_copying.setText("Finished")
        self.show_message("Could not copy the following files:\n" + ''.join([x+"\n" for x in self.activity.unsuccesfull_log]))


    def start_activity(self,B_or_R):
        """starts B or R process
        Args: * bool-> True for Backup and False for Restore"""
        if B_or_R:
            self.activity = BackupActivity()
        else:
            self.activity = RestoreActivity()
        self.activity.update.connect(self.update_progress)
        self.activity.elapsed.connect(self.update_elapsed)
        self.activity.finished.connect(self.finish_ui)
        self.activity.run(self.config)

    def show_message(self,text_to_show):
        self.message_box = QMessageBox()
        self.message_box.setWindowTitle("Warning")
        self.message_box.setIcon(QMessageBox.Information)
        self.message_box.setText(text_to_show)
        self.message_box.setStandardButtons(QMessageBox.Ok)
        self.message_box.exec()
