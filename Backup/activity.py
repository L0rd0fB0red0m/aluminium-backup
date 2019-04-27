from threading import Thread                                                    #for multithreaded copying
import json                                                                     #for parsing and writing used config for restore_config
import zipfile                                                                  #for compression
import shutil                                                                   #for copying
import os                                                                       #for creating directories
import pyAesCrypt                                                               #for encryption
import psutil                                                                   #for os-related things (eg. number of threads)
import datetime                                                                 #for elapsed time

from PyQt5.QtCore import *


class Activity(QThread):
    """"""

    update = pyqtSignal("PyQt_PyObject","PyQt_PyObject")
    elapsed = pyqtSignal("PyQt_PyObject")
    finished = pyqtSignal("PyQt_PyObject")

    def __init__(self):
        """"""
        #super().__init__()
        QThread.__init__(self)


    def run(self, configuration):
        """starts backup process"""
        self.start_time = datetime.datetime.now()
        self.backup_threads = {}
        self.configuration = configuration
        self.backup_src = []
        for dirname in self.configuration["selected_dirs"]:
            for (dirpath,dirnames,files) in os.walk(dirname):
                self.backup_src += [os.path.join(dirpath, file) for file in files]

        self.backup_dest = self.configuration["output_dir"]+"/"

        self.apply_config()
        self.progress = 0
        self.copied_files = []
        self.unsuccesfull_log = []
        self.max_progress = len(self.backup_src)
        self.pause = False

        self.write_config()
        self.transfer_files()

    def apply_config(self):
        """removes elements from the file-list depending on the params set by the user in UI"""
        if self.configuration["ignore_different_ending"]:
            self.backup_src = [x for x in self.backup_src if os.path.splittext(x)[1] in self.configuration["only_ending"]] #only keep entries that match the specified endings
        if self.configuration["set_min_file_size"]:
            self.configuration["min_file_size"] = [1,1024,10240,102400,1048576][["1B","1KB","10KB","100KB","1MB"].index(self.configuration["min_file_size"])]
            #OK this was a tough one: converts the human-readable sizes to their byte-equivalent. If "1KB" was set by the user the second bracket makes 2, selecting 1024 bytes ie. 1KB
            self.backup_src = [x for x in self.backup_src if os.path.getsize(x) >= self.configuration["min_file_size"]] #only keep entries that match the specified size
        if self.configuration["set_max_file_size"]:
            self.configuration["max_file_size"] = [1,1024,10240,102400,1048576][["1B","1KB","10KB","100KB","1MB"].index(self.configuration["max_file_size"])]
            self.backup_src = [x for x in self.backup_src if os.path.getsize(x) <= self.configuration["max_file_size"]] #only keep entries that match the specified size
        if self.configuration["ignore_hidden"]:
            self.backup_src = [x for x in self.backup_src if "/." not in x]                   #removes entries with .filename
        self.encryption_password = self.configuration["encryption_password"]
        if self.configuration["file_list_generator"] != "":
            try:
                exec(open(self.configuration["file_list_generator"]).read())
                self.backup_src = self.backup_src + self.generated_list
            except:
                print("Did not execute user code")


    def compress_1(self):
        """No compression, just copying"""
        while len(self.backup_src)>0:
            if not self.pause:
                try:
                    working_file = self.backup_src[0]
                    del self.backup_src[0]
                    self.copy_single(working_file)
                    self.update_progress(working_file)
                except:
                    print("no more files")


    def compress_2(self):
        """Simple zip compression"""
        while len(self.backup_src)>0:
            if not self.pause:
                working_file = self.backup_src[0]
                del self.backup_src[0]
                self.compress_single(working_file,0)
                self.update_progress(working_file)


    def compress_3(self):
        """lzma compression: slow + most effective"""
        while len(self.backup_src)>0:
            if not self.pause:
                working_file = self.backup_src[0]
                del self.backup_src[0]
                self.compress_single(working_file,1)
                self.update_progress(working_file)


    def compress_single(self,src,format):
        """compresses a single file and passes it tot copy
        Args: * str-> path of file
              * int-> deflatet format: (0:zip),(1:lzma)"""
        compression_method = {"0":zipfile.ZIP_DEFLATED,"1":zipfile.ZIP_LZMA}
        file_extension = [".zip",".lzma"]
        try:
            os.chdir(src[:src.rfind('/')+1])
            temporary_zipfile = zipfile.ZipFile(src+file_extension[format], "w", compression_method[str(format)])
            temporary_zipfile.write(src[src.rfind('/')+1:])
            temporary_zipfile.close()
            self.copy_single(src+file_extension[format])
            os.remove(src+file_extension[format])
        except:
            self.unsuccesfull_log.append("/"+src)
        """stories_zip = zipfile.ZipFile('C:\\Stories\\Funny\\archive.zip')
        for file in stories_zip.namelist():
            stories_zip.extract(file, 'C:\\Stories\\Short\\Funny')
        """


    def copy_single(self,src):
        """copies one given file respecting the params from the configuration
        Args: * str-> path to file"""
        src_dir_name, _ = os.path.split(src)
        try:
            if src[0]=="/":
                src = src[1:]
                src_dir_name = src_dir_name[1:]
            if not os.path.exists(self.backup_dest+src_dir_name):
                try:
                    os.makedirs(self.backup_dest+src_dir_name)
                except FileExistsError:
                    #BUG: when multiple threads try to create the same directory
                    print("Did not create dir (already exists)")

            if self.configuration["encrypt_files"]:
                pyAesCrypt.encryptFile("/" + src, self.backup_dest+src+".aes", self.encryption_password, 65536) #last arg is "buffersize", set to 64Kb
            elif self.configuration["keep_metadata"]:
                shutil.copy2("/"+src,self.backup_dest+src)
            else:
                shutil.copyfile("/"+src,self.backup_dest+src)
        except:
            self.unsuccesfull_log.append("/"+src)


    def transfer_files(self):
        """launches the copying threads by assigning the correct compression method"""
        cores = (psutil.cpu_count())*4
        #4 software threads per hardware thread (I read somewhere that a modern CPU should handle  16)
        self.running = True
        if self.configuration["compression_method"] == 2:
            for work_threads in range(cores):
                self.backup_threads["T_"+str(work_threads)] = Thread(target = self.compress_3)
        elif self.configuration["compression_method"] == 1:
            for work_threads in range(cores):
                self.backup_threads["T_"+str(work_threads)] = Thread(target = self.compress_2)
        else:
            for work_threads in range(cores):
                self.backup_threads["T_"+str(work_threads)] = Thread(target = self.compress_1)
        for i in self.backup_threads:
            self.backup_threads[i].start()
        elapsed_thread = Thread(target=self.update_elapsed)
        elapsed_thread.start()


    def write_config(self):
        """writes the used configuration at the root of the output directory. Used when restoring"""
        config_to_write = {
            "input_size" : self.configuration["input_size"],
            "approx_output_size" :  self.configuration["approx_output_size"],
            "compression_method" :  self.configuration["compression_method"],
            "keep_metadata" : self.configuration["keep_metadata"]
        }
        with open(self.backup_dest + "AlB_config.json","w") as f:
            json.dump(config_to_write,f)
        f.close()


    def update_progress(self,copied_file):
        """"""
        self.progress += 1
        percentage = self.progress / self.max_progress
        self.update.emit(percentage,copied_file)
        if self.progress == self.max_progress:
            self.finished.emit(self.unsuccesfull_log)


    def update_elapsed(self):
        """"""
        while self.progress < self.max_progress:
            if not self.pause:
                self.elapsed.emit(str(datetime.datetime.now() - self.start_time))
