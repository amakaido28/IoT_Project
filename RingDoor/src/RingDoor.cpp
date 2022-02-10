#include <Arduino.h>
#include <LiquidCrystal.h>
#include <Connect.h>
#define PUSH_BUTTON 12

const int rs = 32;
const int en = 33;
const int d4 = 19;
const int d5 = 5;
const int d6 = 17;
const int d7 = 16;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

enum disp_states {
  riposo,
  display
};

int ButtonState;
int current_state = riposo;
int future_state;

unsigned long timer = 0;
int timeout = 20000;

enum states_conn{
  disconnected,
  wifi_connected,
  server_connected
};

int current_state_conn = disconnected;
int data = 0;
uint8_t message[12];
size_t size = 12;


void show_timer(){
  lcd.setCursor(0,1);
  lcd.print("   ");
  lcd.setCursor(0,1);
  lcd.print(String(timeout/1000 - (millis()-timer)/1000));
}


void show_message(){
  lcd.clear();

  if(strcmp((char*) message, "000000000000") == 0)
    lcd.print("Arriva presto");
  else if (strcmp((char*) message, "FFFFFFFFFFFF") == 0)
    lcd.print("Nessun vicino");
  else
    lcd.print((char*) message);
  
  show_timer();
}


void send_mess(){
  timer = millis();

  if(current_state_conn == server_connected){
    writeDataRing(data);
    receiveDataRing(message, size);
  }
  else
    strcpy((char*) message, "FFFFFFFFFFFF");
    
  show_message();
}


void riposo_next(){
  future_state = riposo;

  if(current_state == riposo && ButtonState == 1){
    future_state = display;
    send_mess();
  }
}


void display_next(){
  future_state = display;

  if(millis()-timer<=timeout)
    show_timer();
  if(millis()-timer>timeout){
    future_state = riposo;
    lcd.clear();
    lcd.print("Hello Stranger!");
  }
  if(current_state == display && ButtonState == 1)
    timer = millis();
}


void set_state_disp(){
  if(current_state == riposo)
    riposo_next();
  else if(current_state == display)
    display_next();
}


void set_state_conn(){
  if(current_state_conn==disconnected)
    current_state_conn = disconnect_next();
  else if(current_state_conn==wifi_connected)
    current_state_conn = wifi_next();
  else if(current_state_conn==server_connected)
    current_state_conn = server_next();
}


void setup_env(){
  lcd.begin(16, 2);
  lcd.print("Hello Stranger!");
  pinMode(PUSH_BUTTON, INPUT);
}


void setup() {
  Serial.begin(9600);

  setup_env();

  setup_conn('2');
}


void loop() {
  if(millis()<timer)
    timer = 0;
  
  set_state_conn();
  
  ButtonState = digitalRead(PUSH_BUTTON);
  
  set_state_disp();
  
  current_state = future_state;
}