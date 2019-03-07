from threading import Thread
import subprocess
import json
import zipfile
import shutil
import os
import lzma
import pyAesCrypt
import psutil



class activity():
    def __init__(self,configuration):
        """inits. backup process"""
        self.backup_threads = {}

        self.configuration = configuration
        self.backup_src = []
        for dirname in self.configuration["selected_dirs"]:
            for (dirpath,dirnames,files) in os.walk(dirname):
                self.backup_src += [os.path.join(dirpath, file) for file in files]

        self.backup_dest = self.configuration["output_dir"]+"/"


        self.apply_config()

        self.copied_files = []
        self.max_progress = len(self.backup_src)
        self.pause = False

        self.write_config()
        self.transfer_files()

    def compress_1(self):
        """No compression, just copying"""
        while len(self.backup_src)>0:
            if not self.pause:
                working_file = self.backup_src[0]
                del self.backup_src[0]
                self.copy_single(working_file)

    def compress_2(self):
        """Simple zip compression"""
        while len(self.backup_src)>0:
            if not self.pause:
                working_file = self.backup_src[0]
                del self.backup_src[0]
                self.compress_single(working_file,0)

    def compress_3(self):
        """lzma compression: slow + most effective"""
        while len(self.backup_src)>0:
            if not self.pause:
                working_file = self.backup_src[0]
                del self.backup_src[0]
                self.compress_single(working_file,1)

    def compress_single(self,src,format):
        """"""
        compression_method = {"0":zipfile.ZIP_DEFLATED,"1":zipfile.ZIP_LZMA}
        file_extension = [".zip",".lzma"]
        os.chdir(src[:src.rfind('/')+1])
        temporary_zipfile = zipfile.ZipFile(src+file_extension[format], "w", compression_method[str(format)])
        temporary_zipfile.write(src[src.rfind('/')+1:])
        temporary_zipfile.close()
        self.copy_single(src+file_extension[format])
        os.remove(src+file_extension[format])
        """stories_zip = zipfile.ZipFile('C:\\Stories\\Funny\\archive.zip')
        for file in stories_zip.namelist():
            stories_zip.extract(file, 'C:\\Stories\\Short\\Funny')
        """


    def copy_single(self,src):
        """"""
        #if keep metadata:
        #shutil.copy2(src,dest)
        try:
            if src[0]=="/":
                src = src[1:]
            if not os.path.exists((self.backup_dest+src)[:(self.backup_dest+src).rfind("/")]):
                os.makedirs((self.backup_dest+src)[:(self.backup_dest+src).rfind("/")])


            if self.encrypt_files:
                pyAesCrypt.encryptFile("/" + src, self.backup_dest+src+".aes", self.encryption_password, 65536) #last arg is "buffersize", set to 64K
            else:
                shutil.copyfile("/"+src,self.backup_dest+src)#might have to rm last "/"
        except:
            print("well...",src)
            #add to log



    def transfer_files(self):
        """"""
        cores = psutil.cpu_count() - 1
        print(cores)
        self.running = True
        if self.configuration["compression_method"] == 3:
            for work_threads in range(cores):
                self.backup_threads["T_"+str(work_threads)] = Thread(target = self.compress_3)
        elif self.configuration["compression_method"] == 2:
            for work_threads in range(cores):
                self.backup_threads["T_"+str(work_threads)] = Thread(target = self.compress_2)
        else:
            for work_threads in range(cores):
                self.backup_threads["T_"+str(work_threads)] = Thread(target = self.compress_1)
        for i in self.backup_threads:
            self.backup_threads[i].start()

    def apply_config(self):
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
        self.encrypt_files = self.configuration["encrypt_files"]
        self.encryption_password = self.configuration["encryption_password"]

    def write_config(self):
        config_to_write = {
            "input_size" : self.configuration["input_size"],
            "approx_output_size" :  self.configuration["approx_output_size"],
            "compression_method" :  self.configuration["compression_method"]
        }
        with open(self.backup_dest+"AlB_config.json","w") as f:
            json.dump(config_to_write,f)
        f.close()