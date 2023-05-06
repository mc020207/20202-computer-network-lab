import socket
import struct
import threading
import os
import sys
import random
import time
import importlib
importlib.reload(sys)

packet_struct = struct.Struct('I1024s')

BUF_SIZE = 1024+24
FILE_SIZE = 1024
IP = '172.17.50.166'
SERVER_PORT = 7777

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind((IP, SERVER_PORT))
    string,client_addr = s.recvfrom(BUF_SIZE)
    file_name = string.decode('utf-8')
    f = open(file_name,"wb")
    while True:
        data,client_addr = s.recvfrom(BUF_SIZE)
        unpacked_data = packet_struct.unpack(data)
        end_flag = unpacked_data[0]
        data = unpacked_data[1]
        if end_flag == 0:
            f.write(data)
        else:
            break
        
    s.close()