import socket
import threading
import re
import http.client as http
from getmac import get_mac_address as gma
#mettiamo ciascun gestore di messaggio in un thread diverso, ed ogni thread gestisce la connessione con un singolo client

HEADER=64 #64 bytes
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT='utf-8'
DISCONNECT_MESSAGE="!DISCONNECT" # quando ricevo questo messaggio dal client mi devo disconnettere, perchè se non lo faccio e chiudo la connessione solo dal client
                                 # dalla parte del server la connessione rimane aperta quindi il client non riesce a riconnettersi

#socket.AF_INET -> dice al socket che tipi di ip accettiamo, in questo caso indirizzi ipv4
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(ADDR) # tutto ciò che si connette a questo indirizzo incontrerà il socket

macAddress = gma()

MacMatcher = "[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$"
time_wait = 5

string_server_write = "ec2-3-69-25-163.eu-central-1.compute.amazonaws.com:8000"
string_server_read = "ec2-3-69-25-163.eu-central-1.compute.amazonaws.com:8001"

People = 0

class RingDoorThread(threading.Thread):

    def __init__(self, *args):
        super(RingDoorThread,self).__init__()
        self.conn = args[0]
        self.addr = args[1]
        self.stop = False
        self.lock = threading.Lock()


    def run(self):
        print(f"[NUOVA CONNESSIONE] {self.addr} connesso.")
        connected=True
        while connected:
            try:
                msg=self.conn.recv(10).decode(FORMAT)

                print(f"[{self.addr}]: {msg}")

                message = self.find_package_receiver()
                message = message.replace(":", "")
                print(message)

                self.conn.send(bytes(message.encode(FORMAT)))
                print("message_sent")

            except:
                print(f"[TIMEOUT] sono passati più di {time_wait} secondi")
                if(self.lock.locked()):
                    self.lock.release()

            if self.stop:
                print("[ATTIVATO] self.stop")
                connected=False
            
        self.conn.close()


    def find_package_receiver(self):
        self.lock.acquire()
        global People

        if(People > 0):
            message = "00:00:00:00:00:00"
        else:
            message = self.receive_from_cloud()
        
        self.lock.release()
        return message


    def receive_from_cloud(self):
        try:
            conn = http.HTTPConnection(string_server_read)
            conn.request("GET", "/Receiver", macAddress)

            response = conn.getresponse()
            content_length = int(response.getheader('Content-Length'))
            receiver = response.read(content_length).decode(FORMAT)

        except:
            print("errore")
            receiver = "FF:FF:FF:FF:FF:FF"

        conn.close()
        return receiver



class SonarThread(threading.Thread):

    def __init__(self, *args):
        super(SonarThread,self).__init__()
        self.conn = args[0]
        self.addr = args[1]
        self.stop = False
        self.lock = threading.Lock()


    def run(self):
        print(f"[NUOVA CONNESSIONE] {self.addr} connesso.")
        connected=True
        while connected:
            try:
                # NB: -1 --> uscito, +1--> entrato
                move=int(self.conn.recv(4).decode(FORMAT))
                print(f"[{self.addr}]: {move}")
                
                self.check_presenza(move)

            except:
                print(f"[TIMEOUT] sono passati più di {time_wait} secondi")
                if(self.lock.locked()):
                    self.lock.release()
            
            if self.stop:
                print("[ATTIVATO] self.stop")
                connected=False
            
        self.conn.close()


    def check_presenza(self, move):
        self.lock.acquire()  #per il thread safe
        global People
        print("[CHECK PRESENZA]")
        People+=move

        if People <=0:
            People=0
            self.write_msg_cloud(0)
            print("non ce nessuno in casa")

        if People>=1:
            self.write_msg_cloud(1)
            print("c'è qualcuno in casa")
            
        self.lock.release()


    def write_msg_cloud(self,mess):
        print("[WRITE MSG TO CLOUD]")
        try:
            print("provo a conn")
            conn = http.HTTPConnection(string_server_write)
            conn.request("POST", "/Move", bytes(str(mess) + "+" + macAddress, 'utf-8'))
            response = conn.getresponse()
            print("fatto")

        except:
            print("errore")
        
        conn.close()



def start():
    socket.listen()
    dict={}
    while True:
        conn, addr = socket.accept()
        conn.settimeout(time_wait)
        #posso ricevere i miei dati qua, e controllo che non esista un thread contente quel dispositivo, nel caso esistesse
        #lo elimino e creo un nuovo thread
        mac_recv=False
        while mac_recv!=True :
            mac=conn.recv(19).decode(FORMAT)
            print(mac)
            stri = mac.split('+')
            mac = stri[0]
            id = stri[1]
            print("[MAC RECEIVED]: " + mac)
            if re.match(MacMatcher, mac.lower()): 
                mac_recv=True
                check_mac(mac,dict)
            
        if id == '1' : #(sonars)
            thread = SonarThread(conn,addr)
        
        if id == '2': #(schermo)
            thread = RingDoorThread(conn, addr)

        #inserisco mac e (ip e porta) e conn nel dizionario
        dict[mac]=[conn,thread]
        thread.start()
        print(f"[CONNESSIONI ATTIVE] {threading.activeCount()-1}")
        


def check_mac(mac,dict):
    #controllo che non ci sia un elemento nel dizionario con lo stesso mac
    if mac in dict:
        print("[DISPOSITIVO GIA CONNESSO]: "+ mac)
        print("[DISCONNESSIONE] sto per chiudere la connessione"+ mac)
        #ho un elemento con lo stesso mac, devo uccidere il thread ed eliminare l'elemento
        thread=dict.get(mac)[1]
        thread.stop=True
        print("[CLOSED] thread chiuso correttamente")


print(SERVER)
print("MAC address:", macAddress)
print("[START] inizializzazione server...")
start()