from threading import Thread                                                    #for multithreaded copying
import zipfile                                                                   #for compression
import shutil                                                                   #for copying
import os                                                                       #for creating directories
import pyAesCrypt                                                               #for encryption
import psutil                                                                   #for os-related things (eg. number of threads)
import datetime                                                                 #for elapsed time

from PyQt5.QtCore import *


class Activity(QThread):
    """The whole backup-process: a Thread launched through status"""

    update = pyqtSignal("PyQt_PyObject","PyQt_PyObject")
    elapsed = pyqtSignal("PyQt_PyObject")
    finished = pyqtSignal("PyQt_PyObject")

    def __init__(self):
        super().__init__()


    def run(self,configuration):
        """starts the actual restore process
        Args: * configuration:dict -> contains all the parameters that have to be respected while copying files"""
        self.start_time = datetime.datetime.now()
        self.activity_threads = {}
        self.restore_config = configuration
        self.progress = 0
        self.unsuccesfull_log = []
        self.location_of_backup = self.restore_config["backup_location"]

        self.original_location = []
        for (dirpath,dirnames,filenames) in os.walk(self.restore_config["backup_location"]):
            for filename in filenames:
                if filename != ".backup_config.AlB":
                    self.original_location.append(os.path.join(dirpath,filename).replace(self.location_of_backup,""))
                    #removes the prefix of the backup folder

        self.max_progress = len(self.original_location)
        self.pause = False
        self.transfer_files(self.restore_config["compression_method"])


    def transfer_files(self, compression_method):
        """creates threads and calls adequate transfer method
        Args: * compression_method:int -> 0 for copyied files, 1 and 2 for compression"""
        cores = (psutil.cpu_count())*4
        #4 software threads per hardware thread (I read somewhere that a modern CPU should handle  16)
        if compression_method == 2 or compression_method == 1:
            for work_threads in range(cores):
                self.activity_threads["T_"+str(work_threads)] = Thread(target = self.decompress_1)
        else:
            for work_threads in range(cores):
                self.activity_threads["T_"+str(work_threads)] = Thread(target = self.decompress_0)
        for i in self.activity_threads:
            self.activity_threads[i].start()
        elapsed_thread = Thread(target=self.update_elapsed)
        elapsed_thread.start()


    def decompress_0(self):
        """No decompression, just copying"""
        while len(self.original_location) > 0:
            if not self.pause:
                working_file = self.original_location[0]
                del self.original_location[0]
                self.copy_single(working_file)
                self.update_progress(working_file)


    def decompress_1(self):
        """Zip AND lzma decompression"""
        while len(self.original_location) > 0:
            if not self.pause:
                working_file = self.original_location[0]
                del self.original_location[0]
                self.decompress_single(working_file)
                self.update_progress(working_file)


    def decompress_single(self, dest):
        """Extracts one single file back to its original location
        Args: * dest:str -> where the file will be restored to"""
        dir_name, file_name = os.path.split(dest)
        try:
            if self.restore_config["create_new_dirs"] or os.path_exists(dir_name) and not os.path.exists(dest) or self.restore_config["overwrite_existing"]:
                temporary_zipfile = zipfile.ZipFile(self.location_of_backup + dest)
                temporary_zipfile.extractall(dir_name, pwd=self.restore_config["decryption_password"])
            else:
                self.unsuccesfull_log.append(dest+" (prohibited through configuration)")
        except:
            self.unsuccesfull_log.append(dest)


    def copy_single(self, dest):
        """copies one given file respecting the params from the configuration
        Args: * dest:str -> where the file will be restored to"""
        dir_name, _ = os.path.split(dest)
        backed_up_location = self.location_of_backup + dest

        try:
            try:
                if not os.path.exists(dir_name) and self.restore_config["create_new_dirs"]:
                    os.makedirs(dir_name)
            except FileExistsError:
                #BUG: when multiple threads try to create the same directory
                print("Did not create dir (already exists)")

            if not os.path.exists(dest) or self.restore_config["overwrite_existing"]:
                if self.restore_config["decrypt_files"]:
                    pyAesCrypt.decryptFile(backed_up_location, dest[:dest.rfind(".aes")], self.restore_config["decryption_password"], 65536) #last arg is "buffersize", set to 64K
                elif self.restore_config["keep_metadata"]:
                    shutil.copy2(backed_up_location, dest)
                else:
                    shutil.copy(backed_up_location, dest)
            else:
                self.unsuccesfull_log.append(dest + " (file exists)")
        except:
            self.unsuccesfull_log.append(dest)


    def update_progress(self,copied_file):
        """sends signal to status with current progress
        Args: * copied_file:str -> name of file that was jsut copied"""
        self.progress += 1
        percentage = self.progress / self.max_progress
        self.update.emit(percentage,copied_file)
        if self.progress == self.max_progress:
            self.finished.emit(self.unsuccesfull_log)


    def update_elapsed(self):
        """sends signal to status with time delta til start"""
        while self.progress < self.max_progress:
            if not self.pause:
                self.elapsed.emit(str(datetime.datetime.now() - self.start_time))
