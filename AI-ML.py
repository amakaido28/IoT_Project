from http.server import BaseHTTPRequestHandler, HTTPServer
from random import randint

Mac_lenght=17

host_server = "ec2-3-69-25-163.eu-central-1.compute.amazonaws.com"
port_server = 8002

Mac_noresult = "FF:FF:FF:FF:FF:FF"
FORMAT = 'utf-8'


def AIAlgorithm(MacAdresses):
    AINum = randint(0, (MacAdresses.__len__()-1)*2 + 1)
    if AINum % 2 == 0:
        return MacAdresses[AINum]
    else:
        return Mac_noresult



class requestHttpAI (BaseHTTPRequestHandler):

    def do_GET(self):
        content_length = int(self.headers['Content-Length'])
        MacAdresses = self.rfile.read(content_length).decode(FORMAT).split(" ")
        print(self.path)
        MacAI = Mac_noresult

        try:
          MacAI = AIAlgorithm(MacAdresses)
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

        self.wfile.write(bytes(MacAI, "utf-8"))
        return



def run():   
  server_address = ("127.0.0.1", port_server)  
  httpd = HTTPServer(server_address, requestHttpAI)   
  httpd.serve_forever() 


run()