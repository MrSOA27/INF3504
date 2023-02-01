import os
import socket
import sys
import re


# Vérifie si l'adresse IP entrée est valide
def is_valid_ip(SERVER):
    match = re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', SERVER )
    if match:
        match= re.match(r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', SERVER)
    return match != None

# Vérifie si le port entré est valide
def is_valid_port(PORT):
    match = re.match(r'^50(0[0-9]|[1-4][0-9]|50)$', PORT)
    return match != None

# Exemple d'utilisation
SERVER  = input("Entrez l'adresse IP: ")
if not is_valid_ip(SERVER ):
    sys.exit("Adresse IP non valide")
PORT = input("Entrez le port: ")
if not is_valid_port(PORT):
    sys.exit("Port non valide")


IP = SERVER
PORT = int(PORT)
#IP = socket.gethostbyname(socket.gethostname())
#PORT = 5005
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"



def ls(client, path):
    if not path or path.isspace():
        path = "."
        print(path)
    client.send(f"ls {path}".encode(FORMAT))
    msg = client.recv(SIZE).decode(FORMAT)
    print(msg)

def cd(client, newCurrentPath,currentPath):
    
    if newCurrentPath == "..":
        if currentPath == "root":
            print("You are already in root")
            return currentPath
        else:
            currentPath = currentPath[:currentPath.rfind("/")]
            print(currentPath)
            client.send(f"cd {currentPath}".encode(FORMAT))
            if client.recv(SIZE).decode(FORMAT) == "ok":
                return f"{currentPath}"
            else:
                print("Directory not found")
            return 
    else:
        client.send(f"cd {newCurrentPath}".encode(FORMAT))
        if client.recv(SIZE).decode(FORMAT) == "ok":
            return f"{newCurrentPath}"
        else:
            print("Directory not found")
            return 

def mkdir(client, newDir):
    client.send(f"mkdir {newDir}".encode(FORMAT))
    if client.recv(SIZE).decode(FORMAT) == "ok":
        print("Directory created")
    else:
        print("Directory already exists")

def send_file(client, name, path): #don't know if file should be a path or just the name for now it's just the name
    
    client.send(f"upload {name} {path}".encode(FORMAT))
    
    #open file
    file = open(name , "rb")

    #send file name
    if client.recv(SIZE).decode(FORMAT) == "not ok":
        print("File name already exists")
        file.close()
        return
    
    while True:
        read = file.read(SIZE)
        if not read:
            break
        client.send(read)
    
    file.close
    print("File sent")

def download(client, name, path):
    client.send(f"download {name} {path}".encode(FORMAT))

    if client.recv(SIZE).decode(FORMAT) == "not ok":
        print("File does not exist")
        return
    
    file = open(name, "wb")
    while True :
        write = client.recv(SIZE)
        file.write(write)
        if sys.getsizeof(write) < 1024: #if the size of the data is less than 1024 bytes it means that it is the last data
            break
    file.close()


def client_program():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    currentDir = os.getcwd()

    while True:
        msg = input("-> ")
        if msg == "exit":
            client.send(msg.encode(FORMAT))
            print(client.recv(SIZE).decode(FORMAT))
            break

        elif msg[:2] == "ls":
            ls(client, msg[3:])

        elif msg[:3] == "cd ":
            cd(client, msg[3:], currentDir)
            print(currentDir)

        elif msg[0:6] == "mkdir ":
            print("mkdir")
            mkdir(client, msg[6:])

        elif msg[0:7] == "upload ":#need to verify if the file exists
            print("upload")
            send_file(client, msg[7:], currentDir)
        elif msg[0:9] == "download ":
            print("download")
            #send download command to the server with as a third argument the current directory
            #send the file name to the server
            download(client, msg[9:], currentDir)
            #receive an ok message from the server or an error message
            #receive the file from the server
            #save the file in the client
        else :
            print("Command not found please try again")





if __name__ == '__main__':
    client_program()