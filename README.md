# IoT_Project
# Progetto IoT di consegna corrieri al vicinato.
Parte di sensoristica --> linguaggio C++ per ESP-32, con connessione al bridge tramite Socket e Wi-Fi
Bridge --> server in Python per ricezione di messaggi tramite Socket dagli ESP-32 e invio dei messaggi "puliti" al Cloud
Cloud --> su Amazon AWS EC2 container Docker per il server centrale in Python connesso al DataBase, App Client per il corriere e Bot Telegram per il vicinato
