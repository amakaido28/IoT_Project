#include <Arduino.h>
#include <WiFi.h>
#include <Connect.h>

const char* ssid = "FASTWEB-Famiglia";
const char* password = "Vaiavanticosi3";

const uint16_t port = 5050;
const char* host = "192.168.1.172";

WiFiClient client;

enum states_conn{
  disconnected,
  wifi_connected,
  server_connected
};

int future_state_conn;
int timeout_server = 1000;

uint8_t Mac[6];
char Mac_str[18];
char id;


void writeDataSonar(int data){
  client.print(F(data));
}


void receiveDataRing(uint8_t* message, size_t size){
    client.read(message, size);
}


void writeDataRing(int data){
    client.print(F("Richiesta"));
}


void writeMac(){
  client.print(F(Mac_str));
  client.print(F(id));
}


void initWiFi() {
  //WiFi.mode(WIFI_STA);
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
    //Serial.println("Connected to server successful!");
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
  sprintf(Mac_str, "%02x:%02x:%02x:%02x:%02x:%02x", Mac[0], 
       Mac[1], Mac[2], Mac[3], Mac[4], Mac[5]);
  id = ID;
}