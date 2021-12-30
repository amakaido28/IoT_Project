from http.server import BaseHTTPRequestHandler, HTTPServer
import pymysql

connection = pymysql.connect(host='ec2-18-192-245-67.eu-central-1.compute.amazonaws.com', user='as', password='sa', database='app_db', port=6033)
print("Connected to:", connection.get_server_info())
cursor = connection.cursor()
cursor.execute("show tables")
data = cursor.fetchall()
print(data)

with connection:
    with connection.cursor() as cursor:
        # Read a single record
        query = "UPDATE `JJ` SET `presenza`=False WHERE `nome`=%s"
        cursor.execute(query,('Ama'))
        result = cursor.fetchone()
        print(result)
    connection.commit()


""""
ADDR = "0.0.0.0"
PORT = 8000

class RequestHandler(BaseHTTPRequestHandler):        
    def do_POST(self):
        print(self.path)
        length = int(self.headers['Content-length'])
        print(self.rfile.read1(length))
        self.send_response(200, "OK")
        self.end_headers()
        self.wfile.write(bytes("serverdata",'utf-8'))

print("[EXECUTING....]")
httpd = HTTPServer((ADDR, PORT), RequestHandler)
httpd.serve_forever()
"""