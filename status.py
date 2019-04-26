from threading import Thread                                                    #for UI-Threading
import datetime                                                                 #for elapsed time
import sys                                                                      #for closing the window

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

    def update_elapsed(self):
        self.elapsed_time.setText("Elapsed: "+str(datetime.datetime.now() - self.start_time))


    def finish_ui(self,unsuccesfull_log):
        self.stop_button.setText("QUIT")
        self.label_now_copying.setText("Finished")
        self.show_message("Could not copy the following files:\n" + ''.join([x+"\n" for x in self.activity.unsuccesfull_log]))


    def start_activity(self,B_or_R):
        """starts B or R process
        Args: * bool-> True for Backup and False for Restore"""
        self.start_time = datetime.datetime.now()
        self.update_UI = update_UI()
        self.update_UI.elapsed.connect(self.update_elapsed)
        self.update_UI.update.connect(self.update_progress)
        self.update_UI.finished.connect(self.finish_ui)
        self.update_UI.run(B_or_R,self.config)


    def show_message(self,text_to_show):
        self.message_box = QMessageBox()
        self.message_box.setWindowTitle("Warning")
        self.message_box.setIcon(QMessageBox.Information)
        self.message_box.setText(text_to_show)
        self.message_box.setStandardButtons(QMessageBox.Ok)
        self.message_box.exec()



class update_UI(QThread):
    update = pyqtSignal("PyQt_PyObject","PyQt_PyObject")
    elapsed = pyqtSignal()
    finished = pyqtSignal("PyQt_PyObject")
    def __init__(self):
        QThread.__init__(self)

    def run(self,B_or_R,config):
        print("OK")
        update_progress = Thread(target=self.update_progress)
        if B_or_R:
            self.activity = BA.activity(config)
        else:
            self.activity = RA.activity(config)
        update_progress.start()

    def update_progress(self):
        previous_length = 0
        while self.activity.progress != self.activity.max_progress:
            self.elapsed.emit()
            if len(self.activity.copied_files) != previous_length:
                print(str(datetime.datetime.now()), end="\r")
                percentage = self.activity.progress / self.activity.max_progress
                now_copying = self.activity.copied_files[-1]
                previous_length = len(self.activity.copied_files)
                self.update.emit(percentage, now_copying)

        self.finished.emit(self.activity.unsuccesfull_log)
