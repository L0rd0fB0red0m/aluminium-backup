""" Aluminium Backup - Automatic Backup and Restore
    Copyright (C) 2018  Rémy Moll

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
# Pyinstaller pyinstaller -F -w main.py --uac-admin --add-data=".AlB\icon.ico;.Alb" --add-data=".AlB\aluminium.jpg;.AlB"
import sys                                                                      #for quitting the programm
import json                                                                     #for parsing and reading config. files
import subprocess                                                               #for displaying help (does not work on every distro)

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
#for UI elements

from Backup import ui as backupUI
from Restore import ui as restoreUI
#for individual UI and func. (B/R)

from status import showStatus as showStatus
#for the progression window

from settings import showSettings as showSettings
#for settings

class main_window(QMainWindow):
    """framework, either shows B or R + Menu bars"""

    def __init__(self):
        """sets dims and basic/universal params"""
        super().__init__()
        #calls QMainWindow methods
        self.resize(400,450)
        config = self.load_config()
        if config["dark_mode"]:
            self.setStyleSheet(open(".AlB/dark.qss").read())
        self.setWindowIcon(QIcon('.AlB/icon.ico'))
        self.setWindowTitle("Aluminium Backup - " + config["default_window"])
        #sets the title depending on whether B or R is set as content
        self.menu_bar = self.menuBar()
        self.menu_bar.setStyleSheet("""*{background-image: url(".AlB/aluminium.jpg");}""")
        settings_button = QAction("Settings",self)
        self.menu_bar.addAction(settings_button)
        settings_button.triggered.connect(self.open_settings)
        #help_button = QAction("Help",self)
        #self.menu_bar.addAction(help_button)
        #help_button.triggered.connect(lambda: subprocess.Popen(['xdg-open', "https://github.com/L0rd0fB0red0m/aluminium-backup/blob/master/README.md"]))
        #info_button = QAction("Info",self)
        #self.menu_bar.addAction(info_button)
        #info_button.triggered.connect(lambda: subprocess.Popen(['xdg-open', "https://dfglfa.net/Informatique/bac2019/remy"]))



        if config["default_window"]=="Backup":
            self.switch_button = QAction("Restore",self)
            self.switch_button.triggered.connect(lambda: self.switch_b_r("Restore"))
            self.content_widgets = backupUI.create_widgets()
            self.B_or_R = True
            self.content_widgets.start_button.clicked.connect(self.start_activity)
        else:
            self.switch_button = QAction("Backup",self)
            self.switch_button.triggered.connect(lambda: self.switch_b_r("Backup"))
            self.content_widgets = restoreUI.create_widgets()
            self.B_or_R = False
            self.content_widgets.start_button.clicked.connect(self.start_activity)

        self.menu_bar.addAction(self.switch_button)
        #sets menu-buttons + respective listeners/hooks
        self.setCentralWidget(self.content_widgets)
        #sets the Backup/Restore - UI as only widget


    def open_settings(self):
        """launches setting window (new window) when Menubutton "Settings" clicked"""
        self.settings_window = showSettings()
        self.settings_window.show()


    def switch_b_r(self,switch_to):
        """changes UI and menu-button after a button-press
        Args: * switch_to:str -> either Restore or Backup"""
        self.menu_bar.removeAction(self.switch_button)
        if switch_to == "Restore":
            self.switch_button = QAction("Backup",self)
            self.content_widgets = restoreUI.create_widgets()
            self.switch_button.triggered.connect(lambda: self.switch_b_r("Backup"))
            #lambda because it allows to pass an argument
            self.setWindowTitle("Aluminium Backup - Restore")
            self.B_or_R = False
            self.content_widgets.start_button.clicked.connect(self.start_activity)
        else:
            self.switch_button = QAction("Restore",self)
            self.content_widgets = backupUI.create_widgets()
            self.switch_button.triggered.connect(lambda: self.switch_b_r("Restore"))
            self.setWindowTitle("Aluminium Backup - Backup")
            self.B_or_R = True
            self.content_widgets.start_button.clicked.connect(self.start_activity)
        self.menu_bar.addAction(self.switch_button)
        self.setCentralWidget(self.content_widgets)


    def start_activity(self,parameter):
        """waits for confirmation from the user and launches the status-window which launches the copying
        Args: parameter:QObject -> which button the user has clicked (OK or Cancel) #it's a little strange, because this arg is never passed (but it works)"""
        def user_decision(parameter):
            if "OK" in str(parameter.text()):
                self.close()
                self.dialog = showStatus(self.B_or_R, self.ui_config)
                self.dialog.show()

        self.ui_config = self.content_widgets.generate_config()
        self.dialog = confirmWindow(self.ui_config["approx_output_size"])
        self.dialog.show()
        self.dialog.buttonClicked.connect(user_decision)
        retval = self.dialog.exec_()


    def load_config(self):
        """reads the config. file and saves entries as dict"""
        try:
            with open('.AlB/.config.AlB', 'r') as f:
                config = json.load(f)
        except:
            config={
            "default_window":"Backup",
            "dark_mode":False,
            }
        return config




def create_main_window():
    """opens the Framework window + exit listeners"""
    main_app = QApplication(sys.argv)
    main_win = main_window()
    main_win.show()
    #sys.exit(main_app.exec_())
    main_app.exec()


class confirmWindow(QMessageBox):
    """small confirmation dialog, showing output size"""

    def __init__(self,output_size):
        """Shows a warning of the space used and gives the user the option to abort
        Args: * output_size:list -> Human readable file size: size + unit as to separate entries"""
        super().__init__()
        self.setText("APPROX. " + str(output_size[0]) + output_size[1] + " WILL BE USED")
        self.setIcon(QMessageBox.Warning)
        self.setWindowTitle("Proceed?")
        self.setEscapeButton(QMessageBox.Cancel)
        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)




"""Actual start"""#################################################################
if __name__ == "__main__":
    #does not run when imported as a module
    create_main_window()

## Wanna hear a hilarious joke?
## This code is self explanatory
