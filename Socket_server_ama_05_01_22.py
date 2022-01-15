import socket
import threading
import re
import http.client as http
import uuid
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

macAddress = hex(uuid.getnode())
time_wait = 2
string_server_write = "ec2-3-69-25-163.eu-central-1.compute.amazonaws.com:8000"
string_server_read = "ec2-3-69-25-163.eu-central-1.compute.amazonaws.com:8001"

People = 0

class RingDoorThread(threading.Thread):

    def __init__(self, *args):
        super(RingDoorThread,self).__init__()
        self.conn = args[0]
        self.addr = args[1]
        self.stop = False


    def run(self):
        print(f"[NUOVA CONNESSIONE] {self.addr} connesso.")
        connected=True
        while connected:
            try:
                msg=self.conn.recv(6).decode(FORMAT)
                if msg==DISCONNECT_MESSAGE:
                    connected=False

                print(f"[{self.addr}]: {msg}")
                message = self.find_package_receiver(msg)
                self.conn.send(message).encode(FORMAT)
            except:
                print("[TIMEOUT] sono passati più di due secondi")

            if self.stop:
                print("[ATTIVATO] self.stop")
                connected=False
            
        self.conn.close()


    def find_package_receiver(self, msg):
        global People

        if(People > 0):
            message = "000000"
        else:
            message = self.receive_from_cloud(msg)
        return message


    def receive_from_cloud(self, msg):
        conn = http.HTTPConnection("127.0.0.1:8081")
        conn.request("GET", "/Receiver", msg)
        response = conn.getresponse()
        receiver = response.read(6).decode(FORMAT)
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
                # mi aspetto di ricevere ogni messaggio come "-1+MAC" oppure "1+MAC", cioè 20 caratteri.
                # NB: -1 --> uscito, +1--> entrato
                move=float(self.conn.recv(2).decode(FORMAT))
                mac=self.conn.recv(17).decode(FORMAT)
                # divido il messaggio di entrata/uscita dal mac address
                #splitted=msg.split("+")
                print("messaggio ricevuto")
                print(move)
                print(mac)
                #move=float(splitted[0])
                #mac=splitted[1]
                self.check_presenza(move,mac)
                print(f"[{self.addr}]: {move}")
            except:
                print("[TIMEOUT] sono passati più di due secondi")
            #msg=conn.recv(msg_length)
            
            if self.stop:
                print("[ATTIVATO] self.stop")
                connected=False
            
            #ma se volessimo mandare delle informazioni dal server al client
            #conn.send("Messaggio ricevuto").encode(FORMAT)
        self.conn.close()


    def check_presenza(self, move,mac):
        self.lock.acquire()  #per il thread safe
        global People
        print("[CHECK PRESENZA]")
        People+=move

        if People <=0:
            People=0
            self.write_msg_cloud(move,mac)
            print("non ce nessuno in casa")

        if People>=1:
            self.write_msg_cloud(move,mac)
            print("c'è qualcuno in casa")
            
        self.lock.release()


    def write_msg_cloud(self,move,mac):
        print("[WRITE MSG TO CLOUD]")
        conn = http.HTTPConnection(string_server_write)
        conn.request("POST", "/Move", str(move)+"+"+mac)
        response = conn.getresponse()
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
            mac=conn.recv(17).decode(FORMAT)
            print("[MAC RECEIVED]: " + mac)
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()): #https://stackoverflow.com/questions/7629643/how-do-i-validate-the-format-of-a-mac-address
                mac_recv=True
                check_mac(mac,dict)
            
        #id = conn.recv(1).decode(FORMAT)
        #if id == '1' : (sonars)
        thread = SonarThread(conn,addr)
        
        #if id == '2': (schermo)
        #thread = RingDoorThread(conn, addr)

        #inserisco mac e (ip e porta) e conn nel dizionario
        dict[mac]=[conn,thread]
        thread.start()
        print(f"[CONNESSIONI ATTIVE] {threading.activeCount()-1}")
        

def check_mac(mac,dict):
    #controllo che non ci sia un elemento nel dizionario con lo stesso mac
    if mac in dict:
        print("[DISPOSITIVO GIA CONNESSO]: "+ mac)
        print("[DISCONNESSIONE] sto per chiudere la connessione"+ mac)
        #ho un elemento con lo stesso mac, devo chiudere la connessione, uccidere il thread ed eliminare l'elemento
        connessione=dict.get(mac)[0]
        thread=dict.get(mac)[1]
        thread.stop=True
        print("[CLOSED] thread chiuso correttamente")


print(SERVER)
print("MAC address:", macAddress)
print("[START] inizializzazione server...")
start()




