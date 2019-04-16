from threading import Thread                                                    #for multithreaded copying
import zipfile                                                                  #for compression
import shutil                                                                   #for copying
import os                                                                       #for creating directories
import pyAesCrypt                                                               #for encryption
import psutil                                                                   #for os-related things (eg. number of threads)




class activity():
    def __init__(self,restore_config):
        """inits. restore process"""
        self.restore_threads = {}
        self.restore_config = restore_config
        self.progress = 0
        self.location_of_backup = self.restore_config["backup_location"]
        self.original_location = []
        for (dirpath,dirnames,filenames) in os.walk(self.restore_config["backup_location"]):
            for filename in filenames:
                if filename != ".config.ALB":
                    self.original_location.append(os.path.join(dirpath,filename).replace(self.location_of_backup,""))

        self.copied_files = []
        self.max_progress = len(self.original_location)
        self.pause = False

        self.apply_config()
        self.transfer_files(self.restore_config["compression_method"])

    def decrypt_file(self):
        """decrypts previously encrypted files"""
        #needs args
        # decrypt:
        pyAesCrypt.decryptFile("/root/Desktop/aluminium_backup/Backup/data.txt.aes", "/root/Desktop/aluminium_backup/Backup/dataout.txt", self.restore_config["decryption_password"], 64 * 1024)


    def transfer_files(self,compression_method):
        """creates threads and calls adequate transfer method"""
        cores = (psutil.cpu_count())*4
        #4 software threads per hardware thread (I read somewhere that a modern CPU should handle  16)
        if compression_method == 3:
            for work_threads in range(cores):
                self.restore_threads["T_"+str(work_threads)] = Thread(target = self.decompress_3)
        elif compression_method == 2:
            for work_threads in range(cores):
                self.restore_threads["T_"+str(work_threads)] = Thread(target = self.decompress_2)
        else:
            for work_threads in range(cores):
                self.restore_threads["T_"+str(work_threads)] = Thread(target = self.decompress_1)
        for i in self.restore_threads:
            self.restore_threads[i].start()


    def decompress_1(self):
        """No decompression, just copying"""
        while len(self.original_location)>0:
            if not self.pause:
                working_file = self.original_location[0]
                del self.original_location[0]
                self.copy_single(working_file)
                self.update_progress(working_file)


    def decompress_2(self):
        """Zip decompression"""
        while len(self.original_location)>0:
            if not self.pause:
                working_file = self.location_of_backup + self.original_location[0]
                del self.original_location[0]
                self.decompress_single(working_file,0)
                self.update_progress(working_file)


    def decompress_3(self):
        """lzma decompression"""
        while len(self.original_location)>0:
            if not self.pause:
                working_file = self.location_of_backup + self.original_location[0]
                del self.original_location[0]
                self.decompress_single(working_file,1)
                self.update_progress(working_file)


    def decompress_single(self,src,format):
        """"""
        os.chdir(src[:src.rfind('/')+1])                                    #moves to the folder the file is in
        temporary_zipfile = zipfile.ZipFile(src)
        for file in temporary_zipfile.namelist():                           #might not need to iterate over list because its only 1 file to start with
            temporary_zipfile.extract(file,src[len(self.location_of_backup):src.rfind("/")])
        #copies back to original location


    def copy_single(self,dest):
        """"""
        #if keep metadata:
        #shutil.copy2(src,dest)
        dir_name, _ = os.path.split(dest)
        try:
            if not os.path.exists(dir_name):
                if self.create_new_dirs:
                    os.makedirs(dir_name)
            shutil.copy(self.location_of_backup+dest,dest)
            if self.decrypt_files:
                pyAesCrypt.decryptFile(self.location_of_backup+dest, dest[:dest.rfind(".aes")], self.restore_config["decryption_password"], 65536) #last arg is "buffersize", set to 64K
            else:
                shutil.copy(self.location_of_backup+dest,dest)
        except:
            print("OUPSI",dest)
            #add to log!!!!!!!!!!!!!!!!!!

    def update_progress(self,copied_file):
        self.progress += 1
        self.copied_files.append(copied_file)

    def apply_config(self):
        self.create_new_dirs = self.restore_config["create_new_dirs"]
        self.overwrite_existing = self.restore_config["overwrite_existing"]
        self.decrypt_files = self.restore_config["decrypt_files"]
        self.decryption_password = self.restore_config["decryption_password"]
