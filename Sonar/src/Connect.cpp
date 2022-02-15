#include <Arduino.h>
#include <WiFi.h>
#include <Connect.h>

const char* ssid = "iPhone Lorenzo";
const char* password = "12345678";

const uint16_t port = 5050;
const char* host = "172.20.10.2";

WiFiClient client;

enum states_conn{
  disconnected,
  wifi_connected,
  server_connected
};

int future_state_conn;
int timeout_server = 800;

uint8_t Mac[6];
char Mac_str_id[20];

char package[4];

void writeDataSonar(int data){
  itoa(data, package, 10);
  client.print(F(package));
}


void receiveDataRing(uint8_t* message, size_t size){
    while(client.read(message, size)==0);

    Serial.println("ricevuto");
    Serial.println((char*) message);
}


void writeDataRing(int data){
    client.print(F("Richiesta"));
}


void writeMac(){
  client.print(F(Mac_str_id));
}


void initWiFi() {
  WiFi.begin(ssid, password);
  Serial.println("Connecting to Wi-Fi...");

  uint8_t retW = WiFi.waitForConnectResult();
  
  if(retW == WL_CONNECTED){
    future_state_conn = wifi_connected;
    Serial.println(WiFi.localIP());
  }
  else{
    future_state_conn = disconnected;
    Serial.println("Failed to connect to Wi-Fi");
  } 
}


void ServerConnection(){
  uint8_t ret = client.connect(host, port, timeout_server);

  if(ret == true){
    future_state_conn=server_connected;
    writeMac();
  }
  else{
    Serial.println("Not connected to server");
    future_state_conn = wifi_connected;
  }
}


int disconnect_next(){
  future_state_conn = disconnected;

  initWiFi();
  if(WiFi.status() == WL_CONNECTED)
    ServerConnection();
  
  return future_state_conn;
}


int wifi_next(){
  future_state_conn = wifi_connected;
  
  if(WiFi.status() != WL_CONNECTED)
    initWiFi();
  if(WiFi.status() == WL_CONNECTED && !client.connected())
    ServerConnection();

  return future_state_conn;
}


int server_next(){
  future_state_conn = server_connected;

  if(WiFi.status() != WL_CONNECTED)
    initWiFi();
  if(WiFi.status() == WL_CONNECTED && !client.connected())
      ServerConnection();
      
  return future_state_conn;
}


void setup_conn(char ID){ 
  WiFi.mode(WIFI_STA);
  WiFi.macAddress(Mac);
  sprintf(Mac_str_id, "%02x:%02x:%02x:%02x:%02x:%02x+%c", Mac[0], 
       Mac[1], Mac[2], Mac[3], Mac[4], Mac[5], ID);
}