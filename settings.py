from PyQt5.QtWidgets import *

class create_window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aluminium Backup - Settings")
        cb = QCheckBox('Show title', self)
        #dropdown "How many threads ~core count"
