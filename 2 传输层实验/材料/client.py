import socket
import struct
import os
import stat
import re
import sys
import time
import random

import FDFTPsocket

CLIENT_PORT = 7777
FILE_SIZE = 1024

packet_struct = struct.Struct('I1024s')

if __name__ == "__main__":
    server_ip="8.218.117.184"
    #file_name = "chain.py"
    file_name = "host_iperf.py"
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    data = (file_name).encode('utf-8')
    server_addr=(server_ip,CLIENT_PORT)
    
    Task = FDFTPsocket.Task(file_name)
    
    #s.sendto(data,server_addr)
    Task.sendto(s,data,server_addr)
    f = open(file_name,"rb")
    while True:
        data = f.read(FILE_SIZE)
        if str(data)!="b''":
            end_flag = 0
            #s.sendto(packet_struct.pack(*(end_flag,data)),server_addr)
            Task.sendto(s,packet_struct.pack(*(end_flag,data)),server_addr)
        else:
            data = 'end'.encode('utf-8')
            end_flag = 1
            #s.sendto(packet_struct.pack(*(end_flag,data)),server_addr)
            Task.sendto(s,packet_struct.pack(*(end_flag,data)),server_addr)
            break
    Task.finish()
    s.close()
