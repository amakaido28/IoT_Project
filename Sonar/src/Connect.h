#ifndef CONNECT_H 
#define CONNECT_H

void setup_conn(char);
int disconnect_next();
int wifi_next();
int server_next();
void writeDataSonar(int);

#endif