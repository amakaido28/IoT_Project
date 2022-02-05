from http.server import BaseHTTPRequestHandler, HTTPServer
from webbrowser import get
import pymysql
import requests


port_server = 8081
port_db = 6033
host = "ec2-3-69-25-163.eu-central-1.compute.amazonaws.com"
user_db='as'
pass_db='sa'
database_name='app_db'
bot_url = 'http://127.0.0.1:5000/vicino'


FORMAT = 'utf-8'

message_default = '00:00:00:00:00:00'
message_noresult = 'FF:FF:FF:FF:FF:FF'
Mac_lenght = 17



def send_message_bot(data_prop, data_neig):
  chat_id_neig = str(data_neig[4]) 
  chat_id_prop = str(data_prop[3])

  DATA = { 'nome_prop' : data_prop[1], 'cognome_prop' : data_prop[2],
            'chatID_prop' : chat_id_prop, 'nome_neig' : data_neig[1], 
            'cognome_neig' : data_neig[2], 'ind_neig' : data_neig[3], 
            'chatID_neig' : chat_id_neig}

  response = requests.post(url=bot_url, data=DATA)
  print(response)



def get_receiver(id=message_default):
    connection = pymysql.connect(host=host, user='as', password='sa', database='app_db', port=port_db)
    cursor = connection.cursor()
    
    cursor.execute(f"SELECT presenza, nome, cognome, chatID, latitudine, longitudine FROM JJ WHERE MAC='{id}'")
    data_prop = cursor.fetchone()

    if(data_prop[0] == 1):
      connection.close()
      return message_default

    lat_prop = data_prop[4]
    long_prop = data_prop[5]
    cursor.execute(f"SELECT MAC, nome, cognome, indirizzo, chatID FROM JJ WHERE MAC!='{id}' AND presenza=0 AND ST_Distance_Sphere(ST_GeomFromText('POINT({lat_prop} {long_prop})', 4326), ST_SRID(POINT(longitudine, latitudine), 4326))<750")
    data_neig = cursor.fetchone()

    if(data_neig == None):
      connection.close()
      return message_noresult

    send_message_bot(data_prop, data_neig)

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
  server_address = ('127.0.0.1', port_server)  
  httpd = HTTPServer(server_address, requestHttpReceiver)   
  httpd.serve_forever() 


run()