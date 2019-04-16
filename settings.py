from PyQt5.QtWidgets import *
import json
from crontab import CronTab 

class create_window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aluminium Backup - Settings")
        grid = QGridLayout()
        self.setLayout(grid)
        grid.addWidget(QLabel("Default window:"),0,0)
        grid.addWidget(self.dd_default_window(),1,0)
        grid.addWidget(self.cb_keep_metadata(),2,0)
        grid.addWidget(self.cb_run_periodically(),3,0)
        grid.addWidget(self.dd_time_period(),4,0)
        grid.addWidget(self.button_select_config(),5,0)
        grid.addWidget(self.save_button(),6,0)

    def cb_keep_metadata(self):
        self.cb_keep_metadata = QCheckBox('Keep metadata (larger and slower)', self)
        return self.cb_keep_metadata

    def dd_default_window(self):
        self.dd_default_window = QComboBox(self)
        self.dd_default_window.addItem("Backup")
        self.dd_default_window.addItem("Restore")
        return self.dd_default_window

    def cb_run_periodically(self):
        self.cb_run_periodically = QCheckBox('Backup periodically', self)
        return self.cb_run_periodically

    def dd_time_period(self):
        self.dd_time_period = QComboBox(self)
        self.dd_time_period.addItem("Daily")
        self.dd_time_period.addItem("Weekly")
        self.dd_time_period.addItem("Monthly")
        return self.dd_time_period

    def button_select_config(self):
        def file_dialog():
            try:
                self.backup_config_location = str(QFileDialog.getOpenFileName(self, "Select Script","","*.AlB"))
            except:
                self.show_message("No file selected")
        self.button_config_chooser = QPushButton("Select configuration file to use")
        self.button_config_chooser.clicked.connect(file_dialog)
        return self.button_config_chooser

    def save_button(self):
        def save_config():
            config = {
                "default_window" : self.dd_default_window.currentText(),
                "keep_metadata" : self.cb_keep_metadata.isChecked(),
                "run_periodically" : self.cb_run_periodically.isChecked(),
                "time_period" : self.dd_time_period.currentText(),
                "config_location" : self.backup_config_location,
            }
            with open(".config.ALB","w") as f:
                json.dump(config,f)
            f.close()
            if config["run_periodically"]:
                self.setup_cronjob(config["time_period"],config["config_location"])
        save_button = QPushButton("Save")
        save_button.clicked.connect(save_config)
        return save_button

    def show_message(self,text_to_show):
        self.message_box = QMessageBox()
        self.message_box.setWindowTitle("Warning")
        self.message_box.setIcon(QMessageBox.Information)
        self.message_box.setText(text_to_show)
        self.message_box.setStandardButtons(QMessageBox.Ok)
        self.message_box.exec()


    def setup_cronjob(self,time_period,config_location):
        cron = CronTab()
        job = cron.new(command="./Backup/cron_exec.py " + config_location)
        if time_period == "Daily":
            job.day.every(1)
        elif time_period == "Weekly":
            job.day.every(7)
        elif time_period == "Monthly":
            job.month.every(1)
        cron.write()
