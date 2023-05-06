#!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.parser import Parser
import poplib
def sendMail():
    # 第三方 SMTP 服务
    mail_host = "smtp.qq.com"  # 设置服务器
    mail_user = "1140492820@qq.com"  # 用户名
    mail_pass = "XXXXX"  # 口令

    sender = '1140492820@qq.com'
    receivers = ['20307130112@fudan.edu.cn']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    message = MIMEText('Python 邮件发送测试...', 'plain', 'utf-8')
    message['From'] = Header("马成QQ", 'utf-8')
    message['To'] = Header("马成复旦", 'utf-8')

    subject = 'Python SMTP 邮件测试'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 587)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print ("邮件发送成功")
        smtpObj.quit()
    except smtplib.SMTPException:
        print ("Error: 无法发送邮件")


def getMail():
    # 输入邮件地址, 口令和POP3服务器地址:
    email = '1140492820@qq.com'
    password = 'XXXXX'
    pop3_server = 'pop.qq.com'

    # 连接到POP3服务器:
    server = poplib.POP3(pop3_server)

    # 身份认证:
    server.user(email)
    server.pass_(password)

    # list()返回所有邮件的编号:
    resp, mails, octets = server.list()
    # print(resp)

    # 获取最新一封邮件, 注意索引号从1开始:
    resp, lines, octets = server.retr(1)
    print(resp)
    print(lines)
    print(octets)
    server.quit()


sendMail()
# getMail()
