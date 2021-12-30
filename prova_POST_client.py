import http.client as http
import time 

def start():
    while True:
        ciao="ciao baby, sono troppo forte!!"
        conn = http.HTTPConnection("http://ec2-18-192-245-67.eu-central-1.compute.amazonaws.com:8000/")
        conn.request("POST", "/TestUrl", ciao)
        response = conn.getresponse()
        conn.close()
        time.sleep(5)
        
start()
