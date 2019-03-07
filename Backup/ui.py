import datetime
import json                                                                     #for parsing and reading config. files
import os                                                                       #for finding sub-dirs. and size

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
#for UI elements


class create_widgets(QWidget):
    """UI for the B-Window"""
    def __init__(self):
        super().__init__()
        self.dialogs = list()
        #default-config:
        self.backup_config = {
            "ignore_hidden" : False,
            "compression_method" : 1,#no compression
            "ignore_different_ending" : False,
            "only_ending" : [],
            "encrypt_files" : False,
            "encryption_password" : "",
            "set_min_file_size" : False,
            "min_file_size" : 0,
            "set_max_file_size" : False,
            "max_file_size" : 0,
            "approx_output_size" : 0,
            "selected_dirs" : [],
            "output_dir" : "",
            "input_size":0


        }
        self.backup_config["selected_dirs"] = []
        self.input_size = [0,"B"]
        self.approx_output_size = [0,"B"]
        #default values (in special func?)
        self.create_grid_layout()

    def create_grid_layout(self):
        """puts every single widget into a grid, evry widget must be mentionned in this func."""
        grid = QGridLayout()

        #1rst row:
        grid.addWidget(self.file_selector_label(), 0, 0, 1, 2)
        grid.addWidget(self.file_selector(), 1, 0 , 1, 2)
        grid.addWidget(self.create_backup_file_list(), 2, 0, 4, 2)
        grid.addWidget(self.show_input_size(), 6, 0, 1, 2)
        grid.addWidget(self.cb_hidden_files(), 7, 0, 1, 2)
        grid.addWidget(self.cb_file_type(), 8, 0)
        grid.addWidget(self.entry_file_type(), 8, 1)
        grid.addWidget(self.cb_file_larger(), 9, 0)
        grid.addWidget(self.dd_file_larger(), 9, 1)
        grid.addWidget(self.cb_file_smaller(), 10, 0)
        grid.addWidget(self.dd_file_smaller(), 10, 1)
        #keep metadata
        #regexp?

        #2nd row:
        grid.addWidget(self.create_compression_info_label(), 0, 2, 1, 2)
        grid.addWidget(self.create_compression_slider(), 1, 2, 1, 2)
        grid.addWidget(self.create_compression_label(), 2, 2, 1, 2)
        grid.addWidget(self.backup_location_selector(), 3, 2, 1, 2)
        grid.addWidget(self.cb_encrypt_files(), 5, 2, 1, 2)
        grid.addWidget(self.entry_encryption_password(), 6, 2, 1, 2)
        grid.addWidget(self.save_profile_button(), 9, 2, 1, 2)
        grid.addWidget(self.create_backup_button(), 10, 3)
        #some more?
        self.setLayout(grid)

    """Select Ending"""#############################################################
    def entry_file_type(self):
        def update_config():
            self.backup_config["only_ending"] = []
            for i in file_type_entry.text().split(","):
                self.backup_config["only_ending"].append(i)
                """Sanitize Input!!!!!!!!"""
        file_type_entry = QLineEdit()
        file_type_entry.setPlaceholderText("<ending>,<ending>,...")
        file_type_entry.editingFinished.connect(update_config)
        return file_type_entry
    def cb_file_type(self):
        def update_config():
            self.backup_config["ignore_different_ending"] = only_file_type.isChecked()
        only_file_type = QCheckBox("Only files with ending: ...")
        only_file_type.toggled.connect(update_config)
        return only_file_type

    """Select Size"""###############################################################
    def cb_file_larger(self):
        def update_config():
            self.backup_config["set_min_file_size"] = file_larger_cb.isChecked()
        file_larger_cb = QCheckBox("Only files larger than")
        file_larger_cb.toggled.connect(update_config)
        return file_larger_cb
    def dd_file_larger(self):
        def update_config():
            self.backup_config["min_file_size"] = file_larger_dd.currentText()
        file_larger_dd = QComboBox(self)
        file_larger_dd.addItem("1B")
        file_larger_dd.addItem("1KB")
        file_larger_dd.addItem("10KB")
        file_larger_dd.addItem("100KB")
        file_larger_dd.addItem("1MB")
        file_larger_dd.currentIndexChanged.connect(update_config)
        return file_larger_dd

    def cb_file_smaller(self):
        def update_config():
            self.backup_config["set_max_file_size"] = file_smaller_cb.isChecked()
        file_smaller_cb = QCheckBox("Only files smaller than")
        file_smaller_cb.toggled.connect(update_config)
        return file_smaller_cb
    def dd_file_smaller(self):
        def update_config():
            self.backup_config["max_file_size"] = file_smaller_dd.currentText()
        file_smaller_dd = QComboBox(self)
        file_smaller_dd.addItem("1B")
        file_smaller_dd.addItem("1KB")
        file_smaller_dd.addItem("10KB")
        file_smaller_dd.addItem("100KB")
        file_smaller_dd.addItem("1MB")
        file_smaller_dd.currentIndexChanged.connect(update_config)
        return file_smaller_dd

    """Select compression"""########################################################
    def create_compression_info_label(self):
        self.compression_info_label = QLabel()
        self.compression_info_label.setText("Set the compression level you want:")
        return self.compression_info_label
    def create_compression_slider(self):
        self.compression_slider = QSlider(Qt.Horizontal)
        self.compression_slider.setMinimum(1)
        self.compression_slider.setMaximum(3)
        self.compression_slider.setValue(2)
        self.compression_slider.setTickPosition(QSlider.TicksBelow)
        self.compression_slider.setTickInterval(1)
        self.compression_slider.valueChanged.connect(self.update_compression_label)
        return self.compression_slider
    def create_compression_label(self):
        self.compression_label = QLabel()
        self.compression_method = 2
        self.compression_label.setText(["Rapid, no compression","Slower, medium compression","Slowest, best compression"][self.compression_method-1])
        return self.compression_label
    def update_compression_label(self):
        self.compression_method = self.compression_slider.value()
        print(str(self.compression_method))
        self.approx_output_size = [round(self.input_size[0]*[1,0.9,0.8][self.compression_method-1],2),self.input_size[1]]
        self.compression_label.setText(["Rapid, no compression","Slower, medium compression","Slowest, best compression"][self.compression_method-1]+"\n"+"Output size estimated at: "+str(self.approx_output_size[0])+" "+self.approx_output_size[1])
        self.backup_config["compression_method"] = self.compression_method
        self.backup_config["approx_output_size"] = self.approx_output_size

    """Select actual files"""########################################################
    def file_selector_label(self):
        file_selector_label = QLabel()
        file_selector_label.setText("Select the directories you want to be backed up")
        return file_selector_label
    def file_selector(self):
        file_button = QPushButton("Select directory")
        file_button.clicked.connect(self.backup_file_dialog)
        return file_button
    def backup_file_dialog(self):
        def update_backup_file_list():
            self.input_size = get_dir_size(self.backup_config["selected_dirs"],self.backup_config["ignore_different_ending"],self.backup_config["only_ending"])
            self.input_size_label.setText("Size of files: "+str(self.input_size[0])+" "+self.input_size[1])
            self.update_compression_label()
            print(self.backup_config["selected_dirs"])
            self.backup_list.addItem(QListWidgetItem(self.backup_config["selected_dirs"][-1]))
            self.backup_config["input_size"] = self.input_size
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.backup_config["selected_dirs"].append(directory)
        print(self.backup_config["selected_dirs"])
        update_backup_file_list()
    def create_backup_file_list(self):
        self.backup_list = QListWidget()
        return self.backup_list
    def show_input_size(self):
        self.input_size_label = QLabel()
        self.input_size_label.setText("Size of files: "+str(self.input_size[0])+" "+self.input_size[1])
        return self.input_size_label

    """Save profile"""###############################################################
    def save_profile_button(self):
        def save_profile():
            #file dialog?
            self.create_config()
            f = open("backup_config_"+str(datetime.datetime.now().strftime("%d.%m.%y-%H:%M"))+".json","w+")
            json.dump(self.backup_config,f)
            f.close()
        save_profile_button = QPushButton("Save profile")
        save_profile_button.clicked.connect(save_profile)
        return save_profile_button

    """Select backup location (dest)"""#############################################
    def backup_location_selector(self):
        self.location_button = QPushButton("Select backup location")
        self.location_button.clicked.connect(self.backup_location_dialog)
        return self.location_button
    def backup_location_dialog(self):
        try:
            self.backup_config["output_dir"] = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        except:
            print("No directory selected")

    """Select if hidden files"""#####################################################
    def cb_hidden_files(self):
        def update_hidden_cfg():
            self.backup_config["ignore_hidden"] = check_hidden.isChecked()
            print(backup_config)
        check_hidden = QCheckBox("Ignore hidden files")
        check_hidden.toggled.connect(update_hidden_cfg)
        return check_hidden

    """Select encryption"""#########################################################
    def cb_encrypt_files(self):
        def update_cfg_encrypt():
            self.backup_config["encrypt_files"] = encrypt_files.isChecked()
        encrypt_files = QCheckBox("Encrypt data")
        encrypt_files.toggled.connect(update_cfg_encrypt)
        return encrypt_files
    def entry_encryption_password(self):
        self.encryption_password = QLineEdit()
        self.encryption_password.setEchoMode(QLineEdit.Password)
        self.encryption_password.setPlaceholderText("Password")
        return self.encryption_password
    def read_password(self):
        """Does this only when button pressed, most secure way"""
        print("No password?")
        #read Password

    """START Button"""##############################################################
    def create_backup_button(self):
        """Hook in main"""
        self.start_button = QPushButton("Backup!")
        return self.start_button

    """Finalize config. ie. get ready for backup"""#################################
    def generate_config(self):
        """Gets called from main"""
        self.read_password()
        return self.backup_config



def get_dir_size(path_list,ignore_different_ending,specified_ending):
    total_size = 0
    def folder_size(path):
        total = 0
        for entry in os.scandir(path):
            if entry.is_file():
                if ignore_different_ending:
                    if os.path.splitext(entry.name)[2] in specified_ending:
                        total += entry.stat().st_size
                        print(entry.name)
                else:
                    total += entry.stat().st_size
                    print(entry.name)
            elif entry.is_dir():
                total += folder_size(entry.path)
        return total
    for path in path_list:
        total_size += folder_size(path)
    unit = "B"
    if total_size/1024>=1:
        total_size = round(total_size/1024,2)
        unit="KB"
        if total_size/1024>=1:
            total_size = round(total_size/1024,2)
            unit="MB"
            if total_size/1024>=1:
                total_size = round(total_size/1024,2)
                unit="GB"
    return [total_size,unit]
