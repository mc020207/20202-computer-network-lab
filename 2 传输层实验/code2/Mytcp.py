import socket
import threading
import random
import FDFTPsocket
import utils
import random
import time


class Mytcp:
    def __init__(self,addr,task:FDFTPsocket.Task,file_name,modol,timeout=2) -> None:
        self.Window=1
        self.threashold=10000000
        self.resending=0
        self.starttime=0
        self.left=0
        self.addr=addr
        self.task=task
        self.sendsocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.file_name=file_name
        self.modol=modol
        self.BUF_SIZE=1500
        self.timer=None
        self.timeout=timeout
        self.MAX_LENGTH=1400
        self.buf=[]
        self.now=0
        self.numresend=0
    
    def sendptk(self,ptk):
        self.task.sendto(self.sendsocket,ptk,self.addr)
        
    def getptk(self):
        return utils.unpack(self.sendsocket.recv(self.BUF_SIZE))

    # 对于客户端连接的反应，具体是检查客户端是不是在合理的时间内给出第三次握手如果没有就直接释放资源
    # 这个地方对于startcon_timer()内部的参数可能需要根据网络情况动态调整
    # 随后接收用户的请求即可
    def recvconnect(self,socket:socket.socket):
        self.sendsocket=socket
        self.startcon_timer()
        ptk,self.addr=self.sendsocket.recvfrom(self.BUF_SIZE)
        self.timeout=3*(time.time()-self.starttime)
        ptk=utils.unpack(ptk)
        self.stop_timer()
        self.modol=ptk['type']
        self.file_name=ptk['data']

    # 客户端连接服务端的时候的函数
    def connect(self):
        randseq=random.randint(0,10000)
        ptk=utils.pack('H',randseq,-1,'')
        self.buf.append(ptk)
        self.sendptk(ptk)
        self.start_timer()
        ptk=self.getptk()
        self.buf.clear()
        self.stop_timer()
        self.timeout=3*(time.time()-self.starttime)
        print(self.timeout)
        self.addr=(self.addr[0],ptk['data'])
        ptk=utils.pack(self.modol,-1,-1,self.file_name)
        self.sendsocket.close()
        self.sendsocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sendptk(ptk)
        self.buf.append(ptk)
        self.start_timer()

    def recv(self):
        isfirst=True
        f=open(self.file_name,'wb')
        self.now=0
        finish=False
        while True:
            ptk=self.getptk()
            if isfirst:
                self.buf.clear()
                self.buf=[None for i in range(5000)]
                self.stop_timer()
                isfirst=False
            if ptk['seq']-self.now<5000 and ptk['seq']-self.now>=0:
                self.buf[ptk['seq']-self.now]=ptk
            for i in range(5000):
                if self.buf[i]==None:
                    self.buf=self.buf[i:]+[None for j in range(i)]
                    break
                self.now+=1
                ptk=self.buf[i]
                if ptk['type']!='E':
                    f.write(ptk['data'])
                else:
                    finish=True
                if i==5000-1:
                    self.buf=[None for j in range(5000)]
            if self.now%100==0:
                print(self.now)
            ptk=utils.pack('',-1,self.now,'')
            if finish:
                ptk=utils.pack('E',-1,self.now,'')
                self.sendptk(ptk)
                self.sendptk(ptk)
                self.sendptk(ptk)
                break
            self.sendptk(ptk)
        pass

    def send(self):
        f=open(self.file_name,"rb")
        self.task=FDFTPsocket.Task(self.file_name)
        seq=0
        self.numresend=0
        finish=False
        recvack=recvAck(self)
        recvack.start()
        print(self.timeout)
        while True:
            if self.timer==None:
                self.start_timer()
            while seq<self.left+self.Window and finish==False:
                if seq%100==0:
                    print(seq,self.left,self.Window,self.threashold)
                data=f.read(self.MAX_LENGTH)
                if str(data)!="b''":
                    ptk=utils.pack('',seq,-1,data)
                    self.sendptk(ptk)
                    self.buf.append(ptk)
                    seq+=1
                else:
                    self.sendptk(utils.pack('E',seq,-1,''))
                    seq+=1
                    finish=True
                    break
            if finish:
                break
        print("Packet loss rate:",self.numresend/(self.numresend+seq))


    def start_timer(self):
        if self.timer!=None:
            self.timer.cancel()
        self.starttime=time.time()
        self.timer=threading.Timer(self.timeout,self.timeoutresend)
        self.timer.setDaemon(True)
        self.timer.start()
    
    def stop_timer(self):
        if self.timer!=None:
            self.timer.cancel()
        self.timer=None

    def resend(self):
        if self.resending==1:
            return
        # if self.timer==None:
        #     self.start_timer()
        self.resending=1
        # self.stop_timer()
        if len(self.buf):
            print('resend',min(len(self.buf),max(10,self.Window)),utils.unpack(self.buf[0])['seq'])
        idx=0
        while idx<len(self.buf) and idx<max(10,self.Window):
            try:
                self.sendptk(self.buf[idx])
                idx+=1
            except:
                break
        
        self.resending=0
        self.numresend+=idx
        # self.start_timer()
        pass
    
    def timeoutresend(self):
        print('timeoutresend')
        if self.timer!=None:
            self.stop_timer()
        self.threashold=max(1,int(self.Window/2))
        self.Window=1
        self.resend()
        self.start_timer()

    def startcon_timer(self):
        self.starttime=time.time()
        self.timer=threading.Timer(10,self.closeconn)
        self.timer.setDaemon(True)
        self.timer.start()

    def closeconn(self):
        self.sendsocket.close()
        # 一些顾名思义
        print("有坏人客户端欺骗我的感情")
        exit(0)

class recvAck(threading.Thread):
    def __init__(self,mytcp:Mytcp):
        threading.Thread.__init__(self)
        self.mytcp=mytcp
        self.nowack=-1
        self.numack=0
        self.preack=0
    def run(self):
        while True:
            ptk=utils.unpack(self.mytcp.sendsocket.recv(self.mytcp.BUF_SIZE))
            acknum=ptk['ack']
            if acknum%100==0:
                print('recvack:',acknum)
            left=self.mytcp.left
            if self.mytcp.Window<self.mytcp.threashold:
                self.mytcp.Window+=1
            else:
                self.mytcp.Window+=1/(int(self.mytcp.Window))
            if acknum>left :
                self.mytcp.stop_timer()
                self.numack=0
                self.mytcp.buf=self.mytcp.buf[acknum-left:]
                self.mytcp.left=acknum
                self.mytcp.start_timer()
            else:
                if acknum==left:
                    self.numack+=1
                if self.numack>=3 and acknum!=self.preack:
                    self.mytcp.Window=self.mytcp.threashold=max(1,int(self.mytcp.Window/2))
                    self.preack=acknum+11
                    self.numack=0
                    self.mytcp.stop_timer()
                    self.mytcp.resend()
                    self.mytcp.start_timer()
                    pass
                if acknum<=self.preack:
                    self.numack=0
            if ptk['type']=='E':
                self.mytcp.stop_timer()
                print('end!!')
                break