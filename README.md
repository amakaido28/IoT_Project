# IoT_Project: Neighborhood Delivery
# Progetto IoT di consegna spedizioni al vicinato.

Parte di sensoristica --> linguaggio C++ per ESP-32, con connessione al bridge tramite Socket e Wi-Fi.

Bridge --> script in Python per ricezione di messaggi tramite Socket dagli ESP-32 e invio dei messaggi "puliti" al Cloud.

Cloud --> su Amazon AWS EC2 vari container Docker per gli script centrali in Python connessi al DataBase, Web Application per il corriere e Bot Telegram per il vicinato.

