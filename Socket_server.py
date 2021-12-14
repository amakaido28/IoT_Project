import socket
import threading

#mettiamo ciascun gestore di messaggio in un thread diverso, ed ogni thread gestisce la connessione con un singolo client

HEADER=64 #64 bytes
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT='utf-8'
DISCONNECT_MESSAGE="!DISCONNECT" # quando ricevo questo messaggio dal client mi devo disconnettere, perchè se non lo faccio e chiudo la connessione solo dal client
                                # dalla parte del server la connessione rimane aperta quindi il client non riesce a riconnettersi

print(SERVER)

#socket.AF_INET -> dice al socket che tipi di ip accettiamo, in questo caso indirizzi ipv4
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(ADDR) # tutto ciò che si connette a questo indirizzo incontrerà il socket

def handle_client(conn, addr):
    print(f"[NUOVA CONNESSIONE] {addr} connesso.")
    connected=True
    while connected:
        #msg_length=conn.recv(HEADER).decode(FORMAT) # trasforma da byte a stringa con il decode
        msg_length=conn.recv(HEADER)
        if msg_length:
            msg_length=int(msg_length)
            #non sappiamo quanto sarà lungo il messaggio che dobbiamo leggere
            #msg=conn.recv(msg_length).decode(FORMAT)
            msg=conn.recv(msg_length)
            if msg ==DISCONNECT_MESSAGE:
                connected=False
            print(f"[{addr}]: {msg}")
            #ma se volessimo mandare delle informazioni dal server al client
            #conn.send("Messaggio ricevuto").encode(FORMAT)
    conn.close()

def start():
    socket.listen()
    while True:
        conn, addr = socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[CONNESSIONI ATTIVE] {threading.activeCount()-1}")

print("[START] inizializzazione server...")
start()




