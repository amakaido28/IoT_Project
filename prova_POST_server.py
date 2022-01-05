from http.server import BaseHTTPRequestHandler, HTTPServer
import pymysql

ADDR = "0.0.0.0"
PORT = 8000

class RequestHandler(BaseHTTPRequestHandler):        
    def do_POST(self):
        print(self.path)
        length = int(self.headers['Content-length'])
        msg=self.rfile.read1(length)
        #msg = cursor.fetchall()
        #sto ricevendo "0+MAC" oppure "1+MAC"
        #scrittura su db
        splitted=msg.split("+")
        move=splitted[0]
        move=int(move)
        move=bool(move)
        mac=splitted[1]
        connection = pymysql.connect(host='ec2-18-192-245-67.eu-central-1.compute.amazonaws.com', user='as', password='sa', database='app_db', port=6033)
        cursor = connection.cursor()
        with connection:
            with connection.cursor() as cursor:
                query = "UPDATE `JJ` SET `presenza`=%s WHERE `MAC`=%s"
                cursor.execute(query,(move,mac))
                result = cursor.fetchone()
                print(result)
            connection.commit()
        #fine scrittura su db

        self.send_response(200, "OK")
        self.end_headers()
        self.wfile.write(bytes("serverdata",'utf-8'))

print("[EXECUTING....]")
httpd = HTTPServer((ADDR, PORT), RequestHandler)
httpd.serve_forever()