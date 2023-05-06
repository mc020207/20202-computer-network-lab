import socket
import time
from datetime import datetime


def pack(data):
    ans = "POST / 1.0\r\n"
    GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
    time_now = "Date:" + datetime.utcnow().strftime(GMT_FORMAT)
    ans += time_now
    ans += "\r\n\r\n" + data
    return ans


def parsing(data):
    lines, data = data.split('\r\n\r\n')
    lines = lines.split('\r\n')
    line0 = lines[0].split(' ')
    if line0[1] == '501':
        return '输入不符合规范'
    else:
        return data


soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect((socket.gethostname(), 12000))
while True:
    print("请输入一个英文字符串")
    data = input()
    sendMessage = pack(data)
    soc.send(sendMessage.encode('UTF-8'))
    if data == '#quit':
        break
    time.sleep(0.01)
    print(parsing(soc.recv(1024).decode('UTF-8')))
soc.close()
