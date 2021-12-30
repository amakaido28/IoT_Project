#ifndef CONNECT_H 
#define CONNECT_H

void setup_conn();
int disconnect_next();
int wifi_next();
int server_next();
void receiveDataRing(uint8_t *);
void writeDataRing(int);

#endif