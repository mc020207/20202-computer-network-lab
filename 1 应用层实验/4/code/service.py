import socket
import threading
from datetime import datetime


class myThread(threading.Thread):  # 继承父类threading.Thread
    def __init__(self, connectSocket, addr):
        threading.Thread.__init__(self)
        self.connectSocket = connectSocket
        self.addr = addr

    def run(self):
        print(self.addr.__str__() + " 成功建立连接")
        while True:
            data = self.connectSocket.recv(1024).decode('UTF-8')
            if data != '':
                print(self.addr.__str__() + " 发送了报文:")
                print(data)
                success, ans = parsing(data)
                if ans == '#QUIT':
                    break
                self.connectSocket.send(pack(success, ans).encode('UTF-8'))
        self.connectSocket.close()
        print(self.addr.__str__() + " 断开连接")


def pack(success, data):
    ans = "1.0 "
    if success:
        ans += '200 OK\r\n'
    else:
        ans += '501 Not Implemented\r\n'
    GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
    time_now = "Date:" + datetime.utcnow().strftime(GMT_FORMAT)
    ans += time_now
    ans += "\r\n\r\n" + data
    return ans


def parsing(data):
    lines, data = data.split('\r\n\r\n')
    success = True
    ans = ''
    try:
        if data == '':
            success = False
        else:
            for i in data:
                if 'a' <= i <= 'z':
                    ans += i.upper()
                elif "A" <= i <= "Z":
                    ans += i.lower()
                else:
                    ans += i
    except:
        success = False
    return success, ans


ip = socket.gethostname()
port = 12000
serviceSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serviceSocket.bind((ip, port))
serviceSocket.listen(5)
print("服务器成功启动")
while True:
    connectSocket, addr = serviceSocket.accept()
    thread = myThread(connectSocket, addr)
    thread.start()
