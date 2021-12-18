import socket
import threading
import re
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


class WorkerThread(threading.Thread):
    def __init__(self,*args):
        super(WorkerThread,self).__init__()
        self.conn = args[0]
        self.addr = args[1]
        self.stop = False

    def run(self):
        print(f"[NUOVA CONNESSIONE] {self.addr} connesso.")
        connected=True
        while connected:
            try:
                #non sappiamo quanto sarà lungo il messaggio che dobbiamo leggere
                msg=self.conn.recv(17).decode(FORMAT)
                if msg ==DISCONNECT_MESSAGE:
                    connected=False
                print(f"[{self.addr}]: {msg}")
            except:
                print("[TIMEOUT] sono passati più di due secondi")
            #msg=conn.recv(msg_length)
            
            if self.stop:
                print("[ATTIVATO] self.stop")
                connected=False
            
            #ma se volessimo mandare delle informazioni dal server al client
            #conn.send("Messaggio ricevuto").encode(FORMAT)
        self.conn.close()
            

'''def handle_client(conn, addr):
    print(f"[NUOVA CONNESSIONE] {addr} connesso.")
    connected=True
    while connected:
        #non sappiamo quanto sarà lungo il messaggio che dobbiamo leggere
        msg=conn.recv(17).decode(FORMAT)
        #msg=conn.recv(msg_length)
        if msg ==DISCONNECT_MESSAGE:
            connected=False
        print(f"[{addr}]: {msg}")
        #ma se volessimo mandare delle informazioni dal server al client
        #conn.send("Messaggio ricevuto").encode(FORMAT)
    conn.close()'''

def start():
    socket.listen()
    dict={}
    while True:
        conn, addr = socket.accept()
        conn.settimeout(2)
        #posso ricevere i miei dati qua, e controllo che non esista un thread contente quel dispositivo, nel caso esistesse
        #lo elimino e creo un nuovo thread
        mac_recv=False
        while mac_recv!=True :
            mac=conn.recv(17).decode(FORMAT)
            print("[MAC RECEIVED]: " + mac)
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()): #https://stackoverflow.com/questions/7629643/how-do-i-validate-the-format-of-a-mac-address
                mac_recv=True
                #controllo che non ci sia un elemento nel dizionario con lo stesso mac
                if mac in dict:
                    print("[DISPOSITIVO GIA CONNESSO]: "+ mac)
                    print("[DISCONNESSIONE] sto per chiudere la connessione"+ mac)
                    #ho un elemento con lo stesso mac, devo chiudere la connessione, uccidere il thread ed eliminare l'elemento
                    connessione=dict.get(mac)[0]
                    thread=dict.get(mac)[1]
                    thread.stop=True
                    print("[CLOSED] thread chiuso correttamente")
                    #uccidere thread
    
        #inserisco mac e (ip e porta) e conn nel dizionario
        thread = WorkerThread(conn,addr)
        dict[mac]=[conn,thread]
        thread.start()
        print(f"[CONNESSIONI ATTIVE] {threading.activeCount()-1}")
        

print("[START] inizializzazione server...")
start()




