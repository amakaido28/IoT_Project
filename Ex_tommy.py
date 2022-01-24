import http.client as http


conn = http.HTTPConnection("127.0.0.1:8081")
conn.request("GET", "/Receiver", "55:55:55:55:55:55")
response = conn.getresponse()
msg = response.read(17).decode('utf-8')
conn.close()
print(msg)