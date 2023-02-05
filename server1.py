import os
import socket
import sys
import threading
import re
import datetime


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
'''
SERVER  = input("Entrez l'adresse IP: ")
if not is_valid_ip(SERVER ):
    sys.exit("Adresse IP non valide")
PORT = input("Entrez le port: ")
if not is_valid_port(PORT):
    sys.exit("Port non valide")


IP = SERVER
PORT = int(PORT)
'''
def server():
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
    #IP = socket.gethostbyname(socket.gethostname())
    #PORT = 5005
    addr = (IP, PORT)
    return addr
#IP = socket.gethostbyname(socket.gethostname())
#PORT = 5005
#ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"




def send_file(conn, file):
    pass


def ls(conn, path, current_path):
    directories = ""
#    current_path = os.getcwd()
    try:
 #       os.chdir(current_path)
        files = os.listdir(f"{current_path}/{path}")
        for name in files:
            directories += f"\n{name}"
        if directories == "":
            directories = " This directory is empty"
 #       conn.send(current_path.encode(FORMAT))

        conn.send(directories[1:].encode(FORMAT))

    except:
        directories = " directory not found"
        conn.send(directories[1:].encode(FORMAT))

def cd(conn, newPath,currentPath):
    '''
#    nPath=f"{newPath}"
    print(newPath)
    nPath=str(newPath)
    print(nPath)
    files = os.listdir(currentPath)
#    if nPath in files:
    try:
        conn.send("ok".encode(FORMAT))
        os.chdir(nPath)
    except:
        conn.send("not ok".encode(FORMAT))
    '''
    files = os.listdir(currentPath)
    try:
 #       if str(newPath) in files:
        conn.send("ok".encode(FORMAT))
        os.chdir(f"{currentPath}/{newPath}")
    except:
        conn.send("not ok".encode(FORMAT))
        


def mkdir(conn, newDir):
    path="."
    files = os.listdir(path)
    if newDir not in files:
        os.mkdir(f"{path}/{newDir}")
        conn.send("ok".encode(FORMAT))
    else:
        conn.send("not ok".encode(FORMAT))


def receive_file(conn, name, path):
    print(f"Receiving :{name}")
    new_path = path + "/" + name
    files = os.listdir(path)
    if name in files:
        conn.send("not ok".encode(FORMAT))
        return
    
    conn.send("ok".encode(FORMAT))
    file = open(new_path, "wb") #openeing a non existing file will create it
    while True :
        write = conn.recv(SIZE)
        file.write(write)
        if sys.getsizeof(write) < 1024: #if the size of the data is less than 1024 bytes it means that it is the last data
            break
    file.close()
    conn.send("ok".encode(FORMAT))

def send_file(conn, name, path):
    print(f"Checking : {name}")
    files = os.listdir(path)
    if name in files:
        conn.send("ok".encode(FORMAT))
    else:
        conn.send("not ok".encode(FORMAT))
        return
    file = open(path + "/" + name, "rb")
    while True:
        read = file.read(SIZE)
        if not read:
            break
        conn.send(read)
    file.close
    print("File sent")
    conn.send("ok".encode(FORMAT))

def msg_time(ip,port,msg):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d@%H:%M:%S")
    m_time=print(f"[{ip}:{port}-{current_time}]: {msg}")
    return m_time


def handle_client(conn, addr, client_id):
    ip, port = addr
    conn_time=datetime.datetime.now().strftime("%Y-%m-%d@%H:%M:%S")
    print(f"New connection: {ip}:{port}-{conn_time} client id: {client_id}")

    connected = True
    while connected:
#        current_time = datetime.datetime.now().strftime("%Y-%m-%d@%H:%M:%S")
        msg = conn.recv(SIZE).decode(FORMAT)
#        print(f"Message from {addr}: {msg}")
#        print(f"[{ip}:{port}-{current_time}]: {msg}")
        if msg == "exit":
            msg_time(ip,port,msg)
            print(f"Connection from client {client_id} closed ({addr})")
            conn.send("Disconnecteddddddd".encode(FORMAT))
            connected = False
        elif msg[:3] == "ls ":
            msg_time(ip,port,msg)
#            print(f"ls {addr}")
            args1 = msg.split(" ")
            ls(conn, args1[1], args1[2])
#            ls(conn, msg[3:])
        elif msg[0:3] == "cd ":
            '''
            cPath=os.getcwd()
            print(cPath)
            print(f"cd {addr}")
            cd(conn,msg[3:],cPath)
            '''
            msg_time(ip,port,msg)
#            print(f"cd {addr}")
            args = msg.split(" ")
            cd(conn, args[1], args[2])
        elif msg[0:6] == "mkdir ":
            msg_time(ip,port,msg)
#            print(f"mkdir {addr}")
#            print(msg)
            mkdir(conn, msg[6:])
        elif msg[0:7] == "upload ":
            msg_time(ip,port,msg)
#            print(f"upload {addr}")
            args = msg.split(" ")
            receive_file(conn, args[1], args[2])
        elif msg[0:9] == "download ":
            msg_time(ip,port,msg)
#            print(f"download{addr}")
            args = msg.split(" ")
            send_file(conn, args[1], args[2])
        else:
            msg_time(ip,port,msg)
#            print(f"Command not found from {addr}")
            conn.send("Command not found".encode(FORMAT))

    conn.close()


def server_program():
    client_id = 0
    serverr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    IP,PORT= server()
    serverr.bind((IP,PORT))
    serverr.listen()
    print(f"Server started on {IP}:{PORT}")
    print("Waiting for connection...")

    while True:
        conn, addr = serverr.accept()
#        print (conn , addr)
        client_id += 1
        thread = threading.Thread(target=handle_client, args=(conn, addr, client_id))
        thread.start()


if __name__ == '__main__':
    server_program()