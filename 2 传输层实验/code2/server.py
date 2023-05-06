import socket
import struct
import sys
import importlib
import pickle
import utils
import threading
import random
import os
import time
from FDFTPsocket import Task
from Mytcp import Mytcp
importlib.reload(sys)

packet_struct = struct.Struct('I1024s')

BUF_SIZE = 1500
FILE_SIZE = 1024
IP = '172.19.6.185'
SERVER_PORT = 7776

class MyThread(threading.Thread):  # 继承父类threading.Thread
    def __init__(self, addr,socket):
        threading.Thread.__init__(self)
        self.addr = addr
        self.mytcp=Mytcp(addr,Task('server.py'),None,None)
        self.socket=socket

    def run(self):
        # 接受客户端的第三次握手
        self.mytcp.recvconnect(self.socket)
        print('连接成功')
        if self.mytcp.modol == 'S':
            print('准备接收')
            # 如果是客户端希望传输，这里服务端给客户端一个准备好了的指令
            self.mytcp.sendptk(utils.pack('',-1,-1,'ready'))
            st=time.time()
            self.mytcp.recv()
            st=time.time()-st
            print("time:",st,'s')
            print("speed:",os.path.getsize(self.mytcp.file_name)/st/1024,'KB/s')
            print('已经成功接收')
        else:
            print('准备传输')
            # 如果是客户端希望接收，那么服务端直接开始传输
            st=time.time()
            self.mytcp.send()
            st=time.time()-st
            print("time:",st,'s')
            print("speed:",os.path.getsize(self.mytcp.file_name)/st/1024,'KB/s')
            print('传输完成')
            self.mytcp.timeout=0.2
        self.mytcp.task.finish()
        os.system("md5sum "+self.mytcp.file_name)
        


def testport(PORT):
    presocket=None
    try:
        presocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        presocket.bind((IP,PORT))
        return presocket
    except:
        if presocket!=None:
            presocket.close()
        return None

def getnewsocket():
    PORT=random.randint(7778,20000)
    presocket=testport(PORT)
    while presocket==None:
        PORT=random.randint(7778,20000)
        presocket=testport(PORT)
    return PORT,presocket

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind((IP, SERVER_PORT))
    while True:
        ptk,addr=s.recvfrom(BUF_SIZE)
        ptk=pickle.loads(ptk)
        if ptk['type']!='H':
            continue
        # 得到一个客户端的请求，选择一个可以使用的端口给这个客户端使用
        PORT,newsocket=getnewsocket()
        thread=MyThread(addr,newsocket)
        thread.start()
        # 将选择的端口告诉请求的客户端
        ptk=utils.pack('B',-1,ptk['seq'],PORT)
        s.sendto(ptk,addr)