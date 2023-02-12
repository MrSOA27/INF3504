import os
import socket
import sys
import threading
import re
import datetime

SIZE = 1024
FORMAT = "utf-8"

'''This function will validate the ip address'''
def is_valid_ip(SERVER):
    match = re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', SERVER )
    if match:
        match= re.match(r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', SERVER)
    return match != None

'''This function will validate the port, the port should be between 5000 and 5050'''
def is_valid_port(PORT):
    match = re.match(r'^50(0[0-9]|[1-4][0-9]|50)$', PORT)
    return match != None

'''This function will hundle the IP and the PORT and prevent any error may  occur'''
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
    address = (IP, PORT)
    return address

'''This function will handle the ls Linux command, so it will receive connection , path ,  current path ass parameter and return nothing, 
it will send the list of directories to the client, and directory not found in case not directory is found'''
def ls(connection, path, currentPath):
    directories = ""
    try:
        files = os.listdir(f"{currentPath}/{path}")
        for file in files:
            directories += f"\n{file}"
        if directories == "":
            directories = "This directory is empty"
        connection.send(directories[1:].encode(FORMAT))
    except:
        directories = "Directory not found"
        connection.send(directories[1:].encode(FORMAT))

'''
This fucntion will handle the cd Linux command (change directory) and send ok if the changing has been succesdfully otherwise, will not ok 
'''
def cd(connection, newPath,currentPath):
    try:
        connection.send("ok".encode(FORMAT))
        os.chdir(f"{currentPath}/{newPath}")
    except:
        connection.send("not ok".encode(FORMAT))

'''
This function will handle mkdir Linux command (make directory command), this command will create a new directory by the name of "newDirectory" 
and print Unable to create the directory in case of failure of creating for any raison
'''
def mkdir(connection, newDirectory):
    try:
        path="."
        files = os.listdir(path)
        if newDirectory not in files:
            os.mkdir(f"{path}/{newDirectory}")
            connection.send("ok".encode(FORMAT))
        else:
            connection.send("not ok".encode(FORMAT))
    except:
        connection.send("not ok".encode(FORMAT))
        print("Unable to create the directory")

'''
This fucntion will handle uploading the documents from the client's to the server's side 
'''
def upload(connection, fileName, path):
    print(f"Receiving... :{fileName}")
    new_path = path + "/" + fileName
    files = os.listdir(path)
    if fileName in files:
        connection.send("not ok".encode(FORMAT))
        return
    connection.send("ok".encode(FORMAT))
    file = open(new_path, "wb")
    while True :
        write = connection.recv(SIZE)
        file.write(write)
        if sys.getsizeof(write) < 1024:
            break
    file.close()
#    connection.send("ok".encode(FORMAT))
    
'''
This fucntion will handle downloading the documents from the server to the client's side 
'''
def download(connection, fileName, path):
    print(f"Checking... : {fileName}")
    files = os.listdir(path)
    print(files)
    if fileName in files:
        connection.send("ok".encode(FORMAT))
        print("ok")
        file = open(path + "/" + fileName, "rb")
        while True:
            read = file.read(SIZE)
            if not read:
                break
            connection.send(read)
        file.close
        print("File sent")
#        connection.send("ok".encode(FORMAT))
    else:
        connection.send("not ok".encode(FORMAT))
        print("not ok")
        return


'''
    This fucntion will return a IP:PORT-current-time : msg  received by the client,          
'''
def msg_time(ip,port,msg):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d@%H:%M:%S")
    m_time=print(f"[{ip}:{port}-{current_time}]: {msg}")
    return m_time

'''
This code defines a client_handler function that serves as a handler for client connections in a server. 
The function takes three arguments: connection, address, and client_id. The connection argument is a socket 
object that is connected to the client, address is a tuple of the client's IP address and port number, 
and client_id is an identifier for the client. The code initializes a connection_time variable with the current date and time, 
and then prints a message indicating a new connection with the client's IP and port number and the connection time.
'''

def client_handler(connection, address, client_id):
    ip, port = address
    connection_time=datetime.datetime.now().strftime("%Y-%m-%d@%H:%M:%S")
    print(f"New connection: {ip}:{port}-{connection_time} client id: {client_id}")
    connected = True
    while connected:
        msg = connection.recv(SIZE).decode(FORMAT)
        if msg == "exit":
            msg_time(ip,port,msg)
            print(f"Connection from client {client_id} closed ({address})")
            connection.send("Disconnected".encode(FORMAT))
            connected = False
        elif msg[:3] == "ls ":
            msg_time(ip,port,msg)
            args1 = msg.split(" ")
            ls(connection, args1[1], args1[2])
        elif msg[0:3] == "cd ":
            msg_time(ip,port,msg)
            args = msg.split(" ")
            cd(connection, args[1], args[2])
        elif msg[0:6] == "mkdir ":
            msg_time(ip,port,msg)
            mkdir(connection, msg[6:])
        elif msg[0:7] == "upload ":
            msg_time(ip,port,msg)
            args = msg.split(" ")
            upload(connection, args[1], args[2])
        elif msg[0:9] == "download ":
            msg_time(ip,port,msg)
            args = msg.split(" ")
            download(connection, args[1], args[2])
        else:
            msg_time(ip,port,msg)
            connection.send("Command not found".encode(FORMAT))
    connection.close()

'''
This code defines a server_program function that starts a server. The function initializes a client identifier client_id to 0 
and creates a socket object serverr. It then calls a server function to get the IP address and 
port number of the server and binds the socket to that address and port using the bind method. The socket is then put into 
listening mode using the listen method. The code prints a message indicating that the server has started and is waiting for connections.
'''
def server_program():
    serverr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    IP,PORT= server()
    serverr.bind((IP,PORT))
    serverr.listen()
    print(f"Server started on {IP}:{PORT}")
    print("Waiting for connection...")
    client_id = 0
    while True:
        connection, address = serverr.accept()
        client_id += 1
        thread = threading.Thread(target=client_handler, args=(connection, address, client_id))
        thread.start()

if __name__ == '__main__':
    server_program()