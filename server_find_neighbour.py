from http.server import BaseHTTPRequestHandler, HTTPServer
import http.client as http
import pymysql
import requests


port_server = 8001
port_db = 6033
host = "ec2-3-69-25-163.eu-central-1.compute.amazonaws.com"
user_db='as'
pass_db='sa'
database_name='app_db'
bot_url = 'http://ec2-3-69-25-163.eu-central-1.compute.amazonaws.com:5001/vicino'


FORMAT = 'utf-8'

message_default = '00:00:00:00:00:00'
message_noresult = 'FF:FF:FF:FF:FF:FF'
Mac_lenght = 17



def send_message_bot(data_prop, data_neig):
  if (data_prop == None) or (data_neig == None):
    return
  
  chat_id_neig, chat_id_prop = str(data_neig[4]), str(data_prop[3])

  DATA = { 'nome_prop' : data_prop[1], 'cognome_prop' : data_prop[2],
            'chatID_prop' : chat_id_prop, 'nome_neig' : data_neig[1], 
            'cognome_neig' : data_neig[2], 'ind_neig' : data_neig[3], 
            'chatID_neig' : chat_id_neig}

  response = requests.post(url=bot_url, data=DATA)
  print(response)



def AI_help(data, data_prop):
  candidates = [neig[0] for neig in data]
  msg = " ".join(candidates)

  conn = http.HTTPConnection("ec2-3-69-25-163.eu-central-1.compute.amazonaws.com:8002")
  conn.request("GET", "/AI", bytes(msg, "utf-8"))
  response = conn.getresponse()
  content_length = int(response.getheader('Content-Length'))
  Mac = response.read(content_length).decode('utf-8')
  print(response.status)
  conn.close()

  if(Mac == message_noresult):
    return Mac, None, None
  
  for neig in data:
    if(neig[0] == Mac):
      data_neig = neig
  
  return Mac, data_prop, data_neig



def get_neighbour(id=message_default):
    connection = pymysql.connect(host=host, user='as', password='sa', database='app_db', port=port_db)
    
    cursor = connection.cursor()
    cursor.execute(f"SELECT presenza, nome, cognome, chatID, latitudine, longitudine FROM JJ WHERE MAC='{id}'")
    data_prop = cursor.fetchone()

    if(data_prop[0] == 1):
      connection.close()
      return message_default, None, None

    lat_prop, long_prop = data_prop[4], data_prop[5]

    cursor.execute(f"SELECT MAC, nome, cognome, indirizzo, chatID FROM JJ WHERE MAC!='{id}' AND presenza=1 AND ST_Distance_Sphere(ST_GeomFromText('POINT({lat_prop} {long_prop})', 4326), ST_SRID(POINT(longitudine, latitudine), 4326))<500 ORDER BY ST_Distance_Sphere(ST_GeomFromText('POINT({lat_prop} {long_prop})', 4326), ST_SRID(POINT(longitudine, latitudine), 4326))")
    data_neig = cursor.fetchone()
    
    if(data_neig == None):
      cursor.execute(f"SELECT MAC, nome, cognome, indirizzo, chatID FROM JJ WHERE MAC!='{id}' AND presenza=0 AND ST_Distance_Sphere(ST_GeomFromText('POINT({lat_prop} {long_prop})', 4326), ST_SRID(POINT(longitudine, latitudine), 4326))<500")
      params = cursor.fetchall()
      connection.close()
      return AI_help(params, data_prop)

    connection.close()
    message_ringdoor = str(data_neig[0])

    return message_ringdoor, data_prop, data_neig



class requestHttpReceiver (BaseHTTPRequestHandler):

    def do_GET(self):
        content_length = int(self.headers['Content-Length'])
        id = self.rfile.read(content_length).decode(FORMAT)
        print(self.path)
        message_ringdoor = bytes(message_noresult, 'utf-8')
        data_prop, data_neig = None, None

        try:
          message_ringdoor, data_prop, data_neig = get_neighbour(id)
          message_ringdoor = bytes(message_ringdoor, FORMAT)
          self.send_response(200)
          self.send_header('Content-type','text/html')
          self.send_header('Content-Length', Mac_lenght)
          self.end_headers()

        except:
          print("errore")
          self.send_response(500)
          self.send_header('Content-type','text/html')
          self.send_header('Content-Length', Mac_lenght)
          self.end_headers()

        self.wfile.write(message_ringdoor)
        send_message_bot(data_prop, data_neig)
        return



def run():   
  server_address = (host, port_server)  
  httpd = HTTPServer(server_address, requestHttpReceiver)   
  httpd.serve_forever() 


run()