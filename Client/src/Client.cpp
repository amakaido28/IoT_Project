#include <Arduino.h>
#include <WiFi.h>

const char* ssid = "FASTWEB-Famiglia";
const char* password = "Vaiavanticosi3";
const char* mac = "aa:bb:cc:02:0b:11";

uint8_t Mac[6];
unsigned long previousMillis = 0;
unsigned long interval = 5000;

int current_state;
int future_state;

enum states{
  disconnected,
  wifi_connected,
  server_connected
};

const uint16_t port = 5050;
const char * host = "192.168.1.145";
uint8_t ret = 0;
uint8_t retW = 0;
WiFiClient client;


void initWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("Connecting to Wi-Fi...");

  retW = WiFi.waitForConnectResult();
  
  if(retW == WL_CONNECTED){
    future_state = wifi_connected;
    Serial.println(WiFi.localIP());
  }
  else{
    future_state = disconnected;
    Serial.println("Failed to connect to Wi-Fi");
  } 
}


void ServerConnection(){
  ret = client.connect(host, port);

  if(ret == true){
    Serial.println("Connected to server successful!");
    future_state=server_connected;
  }
  else{
    Serial.println("Not connected to server");
    future_state = wifi_connected;
  }
}


void writeClient(){
  client.print(F((char*) Mac));
}


void disconnect_next(){
  future_state = disconnected;

  initWiFi();
  if(WiFi.status() == WL_CONNECTED)
    ServerConnection();
}


void wifi_next(){
  future_state = wifi_connected;
  
  if(WiFi.status() != WL_CONNECTED)
    initWiFi();
  if(WiFi.status() == WL_CONNECTED && !client.connected())
    ServerConnection();
  if(client.connected())
    future_state = server_connected;
}


void server_next(){
  future_state = server_connected;

  if(WiFi.status() != WL_CONNECTED)
    initWiFi();
  if(WiFi.status() == WL_CONNECTED && !client.connected())
    ServerConnection();
  if(client.connected())
    writeClient();
}


void setup() {
  Serial.begin(9600);
  disconnect_next();
  current_state = future_state;
  WiFi.macAddress(Mac);
}


void loop(){
  unsigned long currentMillis = millis();
  Serial.println(current_state);
  previousMillis = currentMillis;

  if(current_state==disconnected){
    disconnect_next();
  }
  if(current_state==wifi_connected){
    wifi_next();
  }
  if(current_state==server_connected){
    server_next();
  }

  current_state=future_state;
  delay(1000);
}