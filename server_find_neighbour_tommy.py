from http.server import BaseHTTPRequestHandler, HTTPServer
from webbrowser import get
import pymysql
import requests

port_db = 6033
host_db = "ec2-3-69-25-163.eu-central-1.compute.amazonaws.com"
user_db='as'
pass_db='sa'
database_name='app_db'

addr_server = "ec2-3-69-25-163.eu-central-1.compute.amazonaws.com"
port_server = 8001

FORMAT = 'utf-8'
message_default = '00:00:00:00:00:00'
Mac_lenght = 17

def get_receiver(id=message_default):
    connection = pymysql.connect(host=host_db, user='as', password='sa', database='app_db', port=port_db)

    cursor = connection.cursor()
    cursor.execute(f"SELECT presenza, nome, cognome, chatID FROM JJ WHERE MAC='{id}'")
    data_prop = cursor.fetchone()

    if(data_prop[0] == 1):
      connection.close()
      return message_default
    
    cursor.execute(f"SELECT MAC, nome, cognome, indirizzo, chatID FROM JJ WHERE MAC!='{id}' AND presenza=0")
    data_neig = cursor.fetchone()

    if(data_neig == None):
      connection.close()
      return message_default

    chat_id_neig = str(data_neig[4]) #non so se chatID è string o int 
    chat_id_prop = str(data_prop[3])

    URL = 'http://127.0.0.1:5000/vicino'
    DATA = { 'nome_prop' : data_prop[1], 'cognome_prop' : data_prop[2], 'chatID_prop' : chat_id_prop, 'nome_neig' : data_neig[1], 'cognome_neig' : data_neig[2], 'ind_neig' : data_neig[3], 'chatID_neig' : chat_id_neig}
    print(DATA)
    response = requests.post(url=URL, data=DATA)
    print(response)

    #message_neighbour = "Ti arriverà il pacco di " + str(data_prop[1]) + " " + str(data_prop[2])
    #message_prop = "Il tuo pacco è stato inviato a " + str(data_neig[1]) + " " + str(data_neig[2]) + " in " + str(data_neig[3])
    
    #send messages to bot telegram
    #print(message_neighbour)
    #print(message_prop)

    connection.close()
    message_ringdoor = str(data_neig[0])

    return message_ringdoor


class requestHttpReceiver (BaseHTTPRequestHandler):

    def do_GET(self):
        id = self.rfile.read(Mac_lenght).decode(FORMAT)
        print(self.path)
        
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(bytes(get_receiver(id), "utf8"))
        return



def run():   
  server_address = ('127.0.0.1', 8081)  
  httpd = HTTPServer(server_address, requestHttpReceiver)  
  print('http server is running...')  
  httpd.serve_forever() 


run()