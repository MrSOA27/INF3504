import os
import socket
import sys
import re

SIZE = 1024
FORMAT = "utf-8"

'''This function will validate the ip address'''
def is_valid_ip(SERVER):
    try:
        match = re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', SERVER )
        if match:
            match= re.match(r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', SERVER)
        return match != None
    except:
        print("Uknown error has occured")

'''This function will validate the port, the port should be between 5000 and 5050'''
def is_valid_port(PORT):
    try:
        match = re.match(r'^50(0[0-9]|[1-4][0-9]|50)$', PORT)
        return match != None
    except:
        print("Uknown error has occured")

'''This function will hundle the IP and the PORT and prevent any error may  occur'''
def server():
    try:
        while True :
            SERVER  = input("Enter the IP Address of the server: ")
            if not is_valid_ip(SERVER):
                print("IP address is not valide, please try again")
            else:
                break
        while True: 
            PORT = input("Enter the Port of the server: ")
            if not is_valid_port(PORT):
                print("Port is not valide, please try again")
            else:
                break
        IP = SERVER
        PORT = int(PORT)
        address = (IP, PORT)
        return address
    except:
        print("Uknown error has occured")    

'''This function will handle the ls Linux command, so it will receive connection , path ,  current path ass parameter and return nothing, 
it will send the list of directories to the client, and directory not found in case not directory is found'''
def ls(client, path,currentPath):
    try:
        
        if not path or path.isspace():
            ppath = "."
        else:
            ppath=path
        client.send(f"ls {ppath} {currentPath}".encode(FORMAT))
        msg = client.recv(SIZE).decode(FORMAT)
        print(msg)
    except:
        print("Uknown error has occured")
'''
This fucntion will handle the cd Linux command (change directory) and send ok if the changing has been succesdfully otherwise, will not ok 
'''
def cd(client, newCurrentPath,currentPath):
    try:
        if newCurrentPath[:2] == "..":
            if currentPath == "/home":
                print("You are already in home")
                return currentPath
            else:
                currentPath = currentPath[:currentPath.rfind("/")]
                return currentPath
        else:
            client.send(f"cd {newCurrentPath} {currentPath}".encode(FORMAT))
            if client.recv(SIZE).decode(FORMAT) == "ok":
                return f"{currentPath}/{newCurrentPath}"
            else:
                print("Directory not found")
                return currentPath
    except:
        print("Uknown error has occured")

'''
This function will handle mkdir Linux command (make directory command), this command will create a new directory by the name of "newDirectory" 
and print Unable to create the directory in case of failure of creating for any raison
'''
def mkdir(client, newDir):
    try:
        client.send(f"mkdir {newDir}".encode(FORMAT))
        if client.recv(SIZE).decode(FORMAT) == "ok":
            print("Directory created")
        else:
            print("Directory already exists")
    except:
        print("Uknown error has occured")
'''
This fucntion will handle uploading the documents from the client's to the server's side 
'''
def upload(client, file, path):
    try:
        client.send(f"upload {file} {path}".encode(FORMAT))
        file = open(file , "rb")
        if client.recv(SIZE).decode(FORMAT) == "not ok":
            print("File name already exists")
            file.close()
            return
        else :
            while True:
                read = file.read(SIZE)
                if not read:
                    break
                client.send(read)
            file.close
            print("File sent")
    except:
        print("Uknown error has occured")


'''
This fucntion will handle downloading the documents from the server to the client's side 
'''
def download(client, file, path):
    try:
        client.send(f"download {file} {path}".encode(FORMAT))
        if client.recv(SIZE).decode(FORMAT) == "not ok":
            print("File does not exist")
            return    
        else:
            file = open(file, "wb")
            while True :
                write = client.recv(SIZE)
                file.write(write)
                if sys.getsizeof(write) < 1024:
                    break
            file.close()
            print ("File received")
    except:
        print("Uknown error has occured")

'''
This function is a client-side program that communicates with a server over a network using the socket module in Python. 
The program initializes a socket using socket.socket(socket.AF_INET, socket.SOCK_STREAM) and connects to the server 
using client.connect(server()). The server() function returns the IP address and port number of the server. The program then enters an 
infinite loop where it waits for user input and executes different commands based on the input.'''
def client_program():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(server())
        currentDir = "/home"
        while True:
            msg = input("-> ")
            if msg == "exit":
                client.send(msg.encode(FORMAT))
                print(client.recv(SIZE).decode(FORMAT))
                break
            elif msg[:2] == "ls":
                ls(client, msg[3:],currentDir)
            elif msg[:3] == "cd ":
                currentDir=cd(client, msg[3:], currentDir)
                print(currentDir)
            elif msg[0:6] == "mkdir ":
                print("mkdir")
                mkdir(client, msg[6:])
            elif msg[0:7] == "upload ":
                print("uploading...")
                upload(client, msg[7:], currentDir)
            elif msg[0:9] == "download ":
                print("downloading...")
                download(client, msg[9:], currentDir)
            else :
                print("Command not found please try again")
    except:
        print("The IP and/or the port are not valid please try again")
        client_program()


if __name__ == '__main__':
    client_program()