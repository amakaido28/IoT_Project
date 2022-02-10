#include <Arduino.h>
#include <WiFi.h>
#include <Connect.h>
#include <Sonar.h>

enum states_sens {
  riposo,
  inter_out,
  ingresso,
  inter_in,
  uscita,
  stallo
};

int current_state_sens = riposo;

enum states_conn{
  disconnected,
  wifi_connected,
  server_connected
};


int current_state_conn = disconnected;

int presence=0;


void out(){
  presence--;
  if(current_state_conn == server_connected){
    writeDataSonar(presence);
    presence=0;
  }
}


void in(){
 presence++;
  if(current_state_conn == server_connected){
    writeDataSonar(presence);
    presence=0;
  }
}


void print_state_sonar() {
  if (current_state_sens == uscita){
    Serial.println("Uscita");
    out();
  }
  if(current_state_sens == ingresso){
    Serial.println("Ingresso");
    in();
  }
    
  if (current_state_sens == inter_out)
    Serial.println("Stato inter_out");
  if(current_state_sens == inter_in)
    Serial.println("Stato inter_in");
  if (current_state_sens == riposo)
    Serial.println("Stato Riposo");
  if(current_state_sens == stallo)
    Serial.println("Stato Stallo");
}


void set_state_sonar(){
  set_activity();

  if(current_state_sens == riposo)
    current_state_sens = riposo_next();
  else if(current_state_sens == inter_out)
    current_state_sens = inter_out_next();
  else if(current_state_sens == inter_in)
    current_state_sens = inter_in_next();
  else if(current_state_sens == ingresso)
    current_state_sens = ingresso_next();
  else if(current_state_sens == uscita)
    current_state_sens = uscita_next();
  else if(current_state_sens == stallo)
    current_state_sens = stallo_next();
}


void set_state_conn(){
  if(current_state_conn==disconnected)
    current_state_conn = disconnect_next();
  else if(current_state_conn==wifi_connected)
    current_state_conn = wifi_next();
  else if(current_state_conn==server_connected)
    current_state_conn = server_next();
}


void setup(){
  Serial.begin(9600);

  setup_sonar();

  setup_conn('1');
}


void loop(){
  check_timer();

  set_state_conn();

  print_state_sonar();

  set_state_sonar();
  
  delay(300);
  
}