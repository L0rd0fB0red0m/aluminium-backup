import json                                                                     #for parsing and r/w config. files

from PyQt5.QtWidgets import *
#for UI elements


class create_widgets(QWidget):
    """UI for the R-Window"""

    def __init__(self):
        super().__init__()
        self.restore_config = {
            #default values
            "create_new_dirs" : False,
            "overwrite_existing" : False,
            "decrypt_files":False,
            "decryption_password" : "",
            "backup_location" : "",
            "approx_output_size":0,
            "compression_method":"?"
        }

        self.create_grid_layout()


    def create_grid_layout(self):
        """puts every single widget into a grid, every widget must be mentionned in this func."""
        grid = QGridLayout()
        self.setLayout(grid)
        grid.addWidget(self.location_selector(), 0, 0, 1, 2)
        grid.addWidget(self.cb_create_new_dirs(), 1, 0, 1, 2)
        grid.addWidget(self.cb_overwrite_existing(), 2, 0, 1, 2)
        grid.addWidget(self.cb_decrypt(), 3, 0, 1, 1)
        grid.addWidget(self.entry_decryption_password(), 3, 1, 1, 1)
        grid.addWidget(self.start_restore_button(), 4, 0, 1, 2)


    """Backup location"""###########################################################
    def location_selector(self):
        """button that opens a dialog to select the location of the backup-folder"""
        def restore_dir_dialog():
            self.restore_config["backup_location"] = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
            try:
                with open(self.restore_config["backup_location"]+"/.backup_config.AlB","r") as f:
                    old_config = json.load(f)
                f.close()
                self.restore_config["compression_method"] = old_config["compression_method"]
                self.restore_config["approx_output_size"] = old_config["input_size"]
                self.restore_config["keep_metadata"] = old_config["keep_metadata"]
            except:
                self.show_message("No config_file found. Backup might be corrupt")

        file_button = QPushButton("Select Backup-directory")
        file_button.clicked.connect(restore_dir_dialog)
        return file_button


    """Checkboxes"""###############################################################
    def cb_create_new_dirs(self):
        """Checkbox: allow the creation of new diredtories"""
        self.create_new_dirs = QCheckBox("Create new directories if necessary")
        return self.create_new_dirs

    def cb_overwrite_existing(self):
        """Checkbox: allow to overwite files that already exist"""
        self.overwrite_existing = QCheckBox("Overwrite existing data (DANGER)")
        return self.overwrite_existing


    """Decryption Password"""######################################################
    def cb_decrypt(self):
        """Decrypt previously encrypted files or not"""
        self.decrypt_files = QCheckBox("Decrypt files")
        return self.decrypt_files

    def entry_decryption_password(self):
        """allows the user to enter a password"""
        self.decryption_password=QLineEdit()
        self.decryption_password.setEchoMode(QLineEdit.Password)
        self.decryption_password.setPlaceholderText("Decryption password")
        return self.decryption_password


    """START Button"""#############################################################
    def start_restore_button(self):
        """closes UI and launches Status which then launches activity. Hook in main"""
        self.start_button = QPushButton("Restore!")
        return self.start_button


    """Finalize config. ie. get ready for backup"""#################################
    def generate_config(self):
        """reads all params and saves them as a dict. Launched from main"""
        self.restore_config["decrypt_files"] = self.decrypt_files.isChecked()
        self.restore_config["decryption_password"] = self.decryption_password.text()
        self.restore_config["overwrite_existing"]=self.overwrite_existing.isChecked()
        self.restore_config["create_new_dirs"]=self.create_new_dirs.isChecked()
        return self.restore_config


    """For Warnings and Messages"""################################################
    def show_message(self,text_to_show):
        """displays a message_box with a customizable message
        Args: * text_to_show:str -> text that will be displayed"""
        self.message_box = QMessageBox()
        self.message_box.setWindowTitle("Warning")
        self.message_box.setIcon(QMessageBox.Information)
        self.message_box.setText(text_to_show)
        self.message_box.setStandardButtons(QMessageBox.Ok)
        self.message_box.exec()
