#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
    Use paramiko module require three packages
        1、windows to linux, as follow blew:
            `MinGW`: windows system , add 'xx\MinGW\bin' to os path
            `PyCrypto`: install pycrypto, before install paramiko
            `paramiko`: install
            Note: if only `Authentication failed` Error, maybe `username` or `passwd` is incorrect.
        2、linux to linux.
    details can reference the related document with Internet.
"""

import paramiko


class UpServerWin(object):
    def __init__(self, ssh_host, ssh_user, ssh_pwd, ssh_port=22):
        self.__host = ssh_host
        self.__user = ssh_user
        self.__pwd = ssh_pwd
        self.__port = ssh_port
        self.__client = None
        self.__conn = None
        self.__sftp = None

    def __cmd_connect(self):
        if self.__conn is not None:
            self.__conn.close()
            self.__conn = None

        try:
            self.__conn = paramiko.SSHClient()
            self.__conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__conn.connect(self.__host, self.__port, self.__user, self.__pwd)
        except Exception as e:
            print 'connect error:', e
        return self.__conn

    def __client_connect(self):
        if self.__client is not None:
            self.__client.close()

        try:
            self.__client = paramiko.Transport((self.__host, self.__port))
            self.__client.connect(username=self.__user, password=self.__pwd)
            self.__sftp = paramiko.SFTPClient.from_transport(self.__client)
        except Exception as e:
            print 'client connect err:', e
        return self.__sftp

    def exec_command(self, command):
        ssh = self.__cmd_connect()
        stdin, stdout, stderr = ssh.exec_command(command)
        out = stdout.readlines()
        err = stderr.readlines()
        self.disconnect()
        # print out, err

    def put(self, local_path, remote_path, disc_key=True):
        """
            local_path: Absolutely local path. eg: abc.txt
            remote_path: Absolutely server path. eg: /home/daily_news/scf_news/abc.txt
        """
        if self.__sftp is None:
            self.__sftp = self.__client_connect()
        self.__sftp.put(local_path, remote_path)
        if disc_key:
            self.disconnect()

    def get(self, local_path, remote_path, disc_key=True):
        if self.__sftp is None:
            self.__sftp = self.__client_connect()
        self.__sftp.get(remote_path, local_path)
        if disc_key:
            self.disconnect()

    def disconnect(self):
        if self.__conn is not None:
            self.__conn.close()
            self.__conn = None

        if self.__client is not None:
            self.__client.close()
            self.__client = None


if __name__ == '__main__':
    us = UpServerWin('192.168.0.233', 'root', 'chinascope!@#$', 22)
    # us.exec_command('ls')
    # us.put(r'D:\123456.txt', '/opt/112233.txt')
    # us.get(r'F:kfd\kfd.txt', '/opt/112233.txt')
    us.get(r'F:\autumn.tar.gz', '/opt/csf_NEWS/autumn.tar.gz')
    us.disconnect()