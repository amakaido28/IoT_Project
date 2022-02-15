#include <Arduino.h>
#include <Sonar.h>
#include <Connect.h>

#define TRIG_PIN_IN 32
#define ECHO_PIN_IN 33
#define TRIG_PIN_OUT 26 //14
#define ECHO_PIN_OUT 27 //12

float distanza_riposo_in;
float distanza_riposo_out;
float distanza_in;
float distanza_out;

int future_state_sens;
int in_active;
int out_active;
int memory;

enum states_sens {
  riposo,
  inter_out,
  ingresso,
  inter_in,
  uscita,
  stallo
};

int trig_dist = 10;
uint32_t timeout = 3000;
int wait = 1000;
unsigned long timer = 0;


void check_timer(){
    if(millis()<timer)
      timer=0;
}


float get_distance(int ECHO_PIN, int TRIG_PIN){
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  unsigned long tempo = pulseIn(ECHO_PIN, HIGH);
  float distance = 0.03438 * tempo / 2;
  return distance;
}


void setup_sonar(){
  pinMode(TRIG_PIN_IN, OUTPUT);
  pinMode(ECHO_PIN_IN, INPUT);
  pinMode(TRIG_PIN_OUT, OUTPUT);
  pinMode(ECHO_PIN_OUT, INPUT);
  
  digitalWrite(TRIG_PIN_IN, LOW);
  digitalWrite(TRIG_PIN_OUT, LOW);
  
  distanza_riposo_in = get_distance(ECHO_PIN_IN, TRIG_PIN_IN);
  distanza_riposo_out = get_distance(ECHO_PIN_OUT, TRIG_PIN_OUT);

  timer=millis();
}


void  set_activity(){
  distanza_in = get_distance(ECHO_PIN_IN, TRIG_PIN_IN);
  distanza_out = get_distance(ECHO_PIN_OUT, TRIG_PIN_OUT);
  Serial.println(distanza_in);
  Serial.println(distanza_out);
  
  in_active=0;
  out_active=0;
  
  if(distanza_in<=distanza_riposo_in-trig_dist)
    in_active=1;
  if(distanza_out<=distanza_riposo_out-trig_dist)
    out_active=1;
}


int riposo_next(){
  future_state_sens = riposo;
  
  if(millis()-timer<=wait)
    return riposo;
  
  if(in_active == 1){
    future_state_sens=inter_out;
    timer=millis();
  }
  
  if(out_active == 1){
    future_state_sens=inter_in;
    timer=millis();
  }
  
  if(in_active == 1 && out_active == 1)
    future_state_sens = riposo;

  return future_state_sens;
}


int inter_out_next(){
  future_state_sens = inter_out;
  
  if(millis()-timer>=timeout){
    future_state_sens = riposo;
    return riposo;
  }
  
  if(in_active == 1)
    timer=millis();
  
  if(out_active == 1)
    future_state_sens = uscita;
  
  if(in_active == 1 && out_active == 1){
    memory = 0;
    future_state_sens = stallo;
  }

  return future_state_sens;
}


int inter_in_next(){
  future_state_sens = inter_in;
  
  if(millis()-timer>=timeout){
    future_state_sens = riposo; 
    return future_state_sens;
  }
  
  if(out_active == 1)
    timer = millis();
  if(in_active == 1)
    future_state_sens = ingresso;
  if(in_active == 1 && out_active == 1){
    memory = 1;
    future_state_sens = stallo;
  }

  return future_state_sens;
}


int ingresso_next(){
  timer = millis();
  future_state_sens = riposo;
  return future_state_sens;
}


int uscita_next(){
  timer = millis();
  future_state_sens = riposo;
  return future_state_sens;
}


int stallo_next(){
  future_state_sens = stallo;
  
  if(memory == 0){
    if(in_active == 0 && out_active == 1)
      future_state_sens = uscita;
    if(in_active == 1 && out_active == 0)
      future_state_sens = inter_out;
    if(in_active == 0 && out_active == 0)
      future_state_sens = riposo;
  }
  else if(memory == 1){
    if(in_active == 1 && out_active == 0)
      future_state_sens = ingresso;
    if(in_active == 0 && out_active == 1)
      future_state_sens = inter_in;
    if(in_active == 0 && out_active == 0)
      future_state_sens = riposo;
  }	

  return future_state_sens;
}