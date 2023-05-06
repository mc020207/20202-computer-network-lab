import socket
import struct
import time
import os

class Task():
    def __init__(self,file_path):
        self.start_time = time.time()
        self.file_size = os.path.getsize(file_path)
        self.byte_count = 0
        
    def sendto(self,s,data,addr):
        self.byte_count += len(data)
        s.sendto(data,addr)
        
    def finish(self):
        time_consume = time.time()-self.start_time
        goodput = self.file_size / (time_consume*1000)
        print("goodput:"+str(goodput)+"Mbps")
        rate = self.file_size / self.byte_count
        print("score:"+str(goodput*rate))
