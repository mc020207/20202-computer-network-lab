import socket
import struct
import os
import stat
import re
import sys
import time
import random
import pickle
import FDFTPsocket
import utils
from Mytcp import Mytcp
CLIENT_PORT = 7776
FILE_SIZE = 1024
SERVER_IP="8.210.99.245"
packet_struct = struct.Struct('I1024s')

if __name__ == "__main__":
    modol='S'
    file_name="test2.jpg"
    task=FDFTPsocket.Task('client.py')
    mytcp=Mytcp((SERVER_IP,CLIENT_PORT),task,file_name,modol)
    mytcp.connect()
    if modol=='S':
        print(mytcp.getptk())
        mytcp.buf.clear()
        mytcp.stop_timer()
        st=time.time()
        mytcp.send()
        st=time.time()-st
        print("time:",st,'s')
        print("speed:",os.path.getsize(file_name)/st/1024,'KB/s')
    else:
        mytcp.buf.clear()
        st=time.time()
        mytcp.recv()
        st=time.time()-st
        print("time:",st,'s')
        print("speed:",os.path.getsize(file_name)/st/1024,'KB/s')
    mytcp.task.finish()
    os.system("md5sum "+file_name)