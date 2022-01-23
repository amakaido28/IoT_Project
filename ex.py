import http.client as http


conn = http.HTTPConnection("127.0.0.1:8081")
conn.request("GET", "/Receiver", "00:00:5e:00:53:af")
response = conn.getresponse()
msg = response.read(17).decode('utf-8')
conn.close()
print(msg)