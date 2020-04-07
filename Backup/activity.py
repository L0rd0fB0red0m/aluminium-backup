import threading                                                                #for multithreaded copying
import json                                                                     #for parsing and writing used config for restore_config
import zipfile                                                                  #for compression
import shutil                                                                   #for copying
import os                                                                       #for creating directories
import pyAesCrypt                                                               #for encryption
import psutil                                                                   #for os-related things (eg. number of threads)
import datetime                                                                 #for elapsed time
import time                                                                     #same

from PyQt5.QtCore import *


class Activity(QThread):
    """The whole backup-process: a Thread launched through status"""

    update_percentage = pyqtSignal("PyQt_PyObject")
    update_detail = pyqtSignal("PyQt_PyObject")
    elapsed = pyqtSignal("PyQt_PyObject")
    finished = pyqtSignal("PyQt_PyObject")

    def __init__(self,config):
        super().__init__()
        self.backup_config = config

    def run(self):
        """starts the actual backup process
        Args: * configuration:dict -> contains all the parameters that have to be respected while copying files"""
        self.start_time = datetime.datetime.now()
        self.activity_threads = {}

        self.progress = 0
        self.unsuccesfull_log = []
        self.backup_dest = self.backup_config["output_dir"]

        self.backup_src = []
        for dirname in self.backup_config["selected_dirs"]:
            for (dirpath,dirnames,files) in os.walk(dirname):
                self.backup_src += [os.path.join(dirpath, file) for file in files]


        self.pause = False
        self.apply_config()
        self.write_config()
        self.transfer_files()


    def apply_config(self):
        """removes elements from the file-list depending on the params set by the user in UI"""
        #######
        #windows - compat:
        #######
        self.update_detail.emit("Applying configuration:")

        if psutil.WINDOWS:
            self.update_detail.emit("Formatting windows-paths")
            self.backup_src = [x.replace("\\", "/") for x in self.backup_src]
        if self.backup_config["ignore_different_ending"]:
            self.backup_src = [x for x in self.backup_src if os.path.splitext(x)[1] in self.backup_config["only_ending"]]
            #only keep entries that match the specified endings
        if self.backup_config["set_min_file_size"]:
            self.backup_config["min_file_size"] = [1,1024,10240,102400,1048576][["1B","1KB","10KB","100KB","1MB"].index(self.backup_config["min_file_size"])]
            #OK this was a tough one: converts the human-readable sizes to their byte-equivalent. If "1KB" was set by the user the second bracket makes 2, selecting 1024 bytes ie. 1KB
            self.backup_src = [x for x in self.backup_src if os.path.getsize(x) >= self.backup_config["min_file_size"]] #only keep entries that match the specified size
        if self.backup_config["set_max_file_size"]:
            self.backup_config["max_file_size"] = [1,1024,10240,102400,1048576][["1B","1KB","10KB","100KB","1MB"].index(self.backup_config["max_file_size"])]
            self.backup_src = [x for x in self.backup_src if os.path.getsize(x) <= self.backup_config["max_file_size"]] #only keep entries that match the specified size
        if self.backup_config["ignore_hidden"]:
            self.backup_src = [x for x in self.backup_src if "/." not in x]
            #removes entries with .filename
        self.encryption_password = self.backup_config["encryption_password"]
        if self.backup_config["file_list_generator"] != "":
            try:
                exec(open(self.backup_config["file_list_generator"]).read())
                #Kinda dangerous but not prone to "hacking" as the user executes his own code on his own machine
                self.backup_src = self.backup_src + generated_list
            except:
                self.update_detail.emit("Did not execute user code")
        if self.backup_config["use_incremential"]:
            self.update_detail.emit("Applying incremential configuration (purging files)")
            self.apply_incremential()

        self.max_progress = len(self.backup_src)
        self.update_detail.emit("Remaining elements: " + str(self.max_progress))

    def write_config(self):
        """writes the used configuration at the root of the output directory. Used when restoring"""
        config_to_write = {
            "timestamp": datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp(),
            "input_size" : self.backup_config["input_size"],
            "approx_output_size" :  self.backup_config["approx_output_size"],
            "compression_method" :  self.backup_config["compression_method"],
            "keep_metadata" : self.backup_config["keep_metadata"]
        }
        with open(self.backup_dest + "/.backup_config.AlB","w") as f:
            json.dump(config_to_write, f)
        f.close()


    def transfer_files(self):
        """launches the copying threads by assigning the correct compression method"""

        cores = (psutil.cpu_count())*4
        #4 software threads per hardware thread (I read somewhere that a modern CPU should handle up to 16 software threads per HW thread)
        self.update_detail.emit("Initializing " + str(cores) + " threads for copying")
        for work_thread in range(cores):
            if self.backup_config["compression_method"] == 2 or self.backup_config["compression_method"] == 1:
                temp = threading.Thread(target = self.compress_1, args=[self.backup_config["compression_method"]])
            else:
                temp = threading.Thread(target = self.compress_0)

            temp.daemon = True
            self.activity_threads["T_"+str(work_thread)] = temp

        for i in self.activity_threads:
            self.activity_threads[i].start()

        elapsed_thread = threading.Thread(target=self.update_elapsed)
        elapsed_thread.start()



    def compress_0(self):
        """No compression, just copying"""
        while len(self.backup_src)>0:
            if not self.pause:
                working_file = self.backup_src[0]
                del self.backup_src[0]
                self.copy_single(working_file)
                self.update_progress(working_file)


    def compress_1(self, compression):
        """compression lzma/zip
        Args: * compression:int -> 1 for ZIP, 2 for LZMA"""
        while len(self.backup_src) > 0:
            if not self.pause:
                working_file = self.backup_src[0]
                del self.backup_src[0]
                self.compress_single(working_file,compression)
                self.update_progress(working_file)


    def compress_single(self, src, format):
        """compresses a single file and passes it tot copy
        Args: * src:str -> path of file
              * format:int -> deflated format: (0:zip),(1:lzma)"""
        compression_method = [zipfile.ZIP_DEFLATED,zipfile.ZIP_LZMA]
        file_extension = [".zip",".lzma"]
        src_dir_name, file_name = os.path.split(src)
        dest_dir_name = (self.backup_dest + "/" + src_dir_name )[::-1].replace(":","",1)[::-1]
        zipfile_name = (self.backup_dest + "/" + src + file_extension[format-1])[::-1].replace(":","",1)[::-1]

        try:
            if not os.path.exists(dest_dir_name):
                try:
                    os.makedirs(dest_dir_name)
                except FileExistsError:
                    #BUG: when multiple threads try to create the same directory
                    print("Did not create dir (already exists)")
            temporary_zipfile = zipfile.ZipFile(zipfile_name, "w", compression_method[format-1])
            temporary_zipfile.write(src, file_name)
            temporary_zipfile.close()
            if self.backup_config["encrypt_files"]:
                pyAesCrypt.encryptFile(zipfile_name, zipfile_name+".aes", self.encryption_password, 16*1024)
                os.remove(zipfile_name)
                #must encrypt seperately
        except:
            self.update_detail.emit("Failed too compress " + src)
            self.unsuccesfull_log.append(src)
            try:
                os.remove(zipfile_name)
            except:
                pass

    def copy_single(self, src):
        """copies one given file respecting the params from the configuration
        Args: * src:str -> path to file"""
        src_dir_name, _ = os.path.split(src)

        dest_dir = (self.backup_dest + "/" + src_dir_name)[::-1].replace(":","",1)[::-1]
        dest_file_name = (self.backup_dest + "/" + src)[::-1].replace(":","",1)[::-1]
        try:
            if not os.path.exists(dest_dir):
                try:
                    os.makedirs(dest_dir)
                except FileExistsError:
                    #BUG: when multiple threads try to create the same directory
                    self.update_detail.emit("Did not create dir " + dest_dir + " (already exists)")

            if self.backup_config["encrypt_files"]:
                pyAesCrypt.encryptFile(src, dest_file_name + ".aes", self.encryption_password, 16*1024)
                #last arg is "buffersize", set to 16K
            elif self.backup_config["keep_metadata"]:
                shutil.copy2(src, dest_file_name)
            else:
                shutil.copy(src, dest_file_name)
        except:
            self.update_detail.emit("Failed to copy " + src)
            self.unsuccesfull_log.append(src)


    def update_progress(self, copied_file):
        """sends signal to status with current progress
        Args: * copied_file:str -> name of file that was jsut copied"""
        self.progress += 1
        percentage = self.progress / self.max_progress
        self.update_percentage.emit(percentage)
        self.update_detail.emit("Copying " + copied_file)
        if self.progress == self.max_progress:
            self.finished.emit(self.unsuccesfull_log)
            if self.backup_config["shutdown_when_finished"]:
                if psutil.WINDOWS:
                    os.system("shutdown -s")
                else:
                    os.system("shutdown -h now")


    def update_elapsed(self):
        """sends signal to status with time delta til start"""
        while self.progress < self.max_progress:
            if not self.pause:
                time.sleep(1)
                self.elapsed.emit(datetime.datetime.now())


    def apply_incremential(self):
        with open(self.backup_dest+"/.backup_config.AlB","r") as f:
            old_config = json.load(f)
        f.close()
        old_date = old_config["timestamp"]
        self.backup_src = [x for x in self.backup_src if old_date - os.path.getmtime(x) < 0]
