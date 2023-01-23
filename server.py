import socket
import threading
import time
import sys
import re

# Vérifie si l'adresse IP entrée est valide
def is_valid_ip(SERVER ):
    match = re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', SERVER )
    if match:
        match= re.match(r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', SERVER)
    return match != None

# Vérifie si le port entré est valide
def is_valid_port(PORT):
    match = re.match(r'^(5[0-9]{3}|[1-4][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$', PORT)
    return match != None

# Exemple d'utilisation
SERVER  = input("Entrez l'adresse IP: ")
if not is_valid_ip(SERVER ):
    sys.exit("Adresse IP non valide")
PORT = input("Entrez le port: ")
if not is_valid_port(PORT):
    sys.exit("Port non valide")
HEADER = 64
#PORT = 5050
#SERVER = socket.gethostbyname(socket.gethostname())

ADDR = (SERVER,PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def handle_client(conn, addr):
    print("[NEW CONNECTION] {addr} connected. ")
    connected = True

    while connected:
        msg_length = conn.recv(HEADER)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {msg}")
            conn.send("Message received".encode(FORMAT))
    conn.close()


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting")
start()

