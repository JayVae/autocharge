# coding=utf-8

import smtplib, email, sys
from email.message import Message

import sys
from imp import reload

reload(sys)


class myemail:
        def __init__(self):
                self.smtpserver = 'smtp.163.com'
                # self.smtpuser = 'xjtuyjw@163.com'
                # self.smtppass = 'Yejiawei19921121'
                self.smtpuser = 'shihaijie0525@163.com'
                self.smtppass = '1013dd1013'
                self.smtpport = '25'
                self.to = 'shihaijie0525@163.com'
                self.subj = 'charge failed!!'
                pass

        def connect(self):
            "connect to smtp server and return a smtplib.SMTP instance object"
            server = smtplib.SMTP(self.smtpserver, self.smtpport)
            server.ehlo()
            server.login(self.smtpuser, self.smtppass)
            return server


        def sendmessage(self, content):
            "using server send a email"
            server = self.connect()
            msg = Message()
            msg['Mime-Version'] = '1.0'
            msg['From'] = self.smtpuser
            msg['To'] = self.to
            msg['Subject'] = self.subj
            # msg['Date'] = email.Utils.formatdate()  # curr datetime, rfc2822
            msg.set_payload(content)
            try:
                failed = server.sendmail(self.smtpuser, self.to, str(msg))  # may also raise exc
            except Exception as ex:
                print(Exception, ex)
                print('Error - send failed')
                raise Exception
            else:
                print("send success!")

            #
            # to = 'xjtuyjw@163.com'
            # subj = 'title1111'
            # print 'Type message text, end with line="."'
            # text = 'content'
            # #    while True:
            # #        line = sys.stdin.readline()
            # #        if line == '. ': break
            # #        text += line
            # server = connect()
            # sendmessage(server, to, subj, text)

if __name__ == '__main__':
    content = r'卡上余额不足，充值失败！！'
    myemail().sendmessage(content)
