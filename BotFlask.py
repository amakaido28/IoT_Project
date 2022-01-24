from flask import Flask, request
import threading
import requests

import logging
import re
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from geopy.geocoders import Nominatim
import pymysql
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

appname = "IOT - sample1"
app = Flask(appname)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

TOKEN = '5015312055:AAEZTBTeijRVNX-t4WbmKsuwLFlNvrvIAjI'
logger = logging.getLogger(__name__)
connection = pymysql.connect(host='ec2-3-69-25-163.eu-central-1.compute.amazonaws.com', user='as', password='sa', database='app_db', port=6033)

MAC_ADDRESS, NAME, LAST_NAME, LOCATION, RESET = range(5)

nome=''
cognome=''
mac_address=''
latitudine=0.0
longitudine=0.0
indirizzo=''
prova=0






class FlaskThread(threading.Thread):
    def run(self) -> None:
        app.run(port=5000, threaded=True)


class TelegramThread(threading.Thread):
    def run(self) -> None:
        main()

@app.route("/vicino", methods=['POST'])
def proviamo():
    print('è entrato')
    data = request.form
    print(data)
    #nome_prop, cognome_prop, chatID_prop, nome_neig, cognome_neig, ind_neig, chatID_neig
    message_neig = "Ti arriverà il pacco di " + data['nome_prop'] + " " + data['cognome_prop']
    message_prop = "Il tuo pacco è stato inviato a " + data['nome_neig'] + " " + data['cognome_neig'] + " in " + data['ind_neig']
    send_text_neig = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + data['chatID_neig'] + '&parse_mode=Markdown&text=' + message_neig
    send_text_prop = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + data['chatID_prop'] + '&parse_mode=Markdown&text=' + message_prop
    resp_neig = requests.get(send_text_neig)
    resp_prop = requests.get(send_text_prop)
    print(resp_neig.status_code)
    print(resp_prop.status_code)
    return str(resp_neig.status_code)







def start(update: Update, context):
    update.message.reply_text(
        'Ciao!\n'
        "Se non l'hai ancora fatto configura il tuo dispositivo lanciando il seguente comando:\n"
        '/config \n\n'
        'Altri comandi:\n'
        '/reset -> Resetta i dati del dispositivo\n'
    )

def config(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Cominciamo la configurazione!\n'
        'Se inserisci erroneamente un dato annulla la configurazione con il comando /cancel\n'
        'Inserisci il tuo nome'
    )
    return NAME

def getname(update: Update, context: CallbackContext) -> int:
    global nome
    nome = update.message.text
    print(nome)
    update.message.reply_text(
        'Inserisci il tuo cognome'
    )
    return LAST_NAME

def getlast_name(update: Update, context: CallbackContext) -> int:
    global cognome
    cognome = update.message.text
    print(cognome)
    update.message.reply_text(
        'Inserisci l''indirizzo MAC del dispositivo scritto sulla scatola'
    )
    return MAC_ADDRESS


def getmac(update: Update, context: CallbackContext) -> int:
    global mac_address
    mac_address = update.message.text
    if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac_address.lower()): 
        print(mac_address)
        update.message.reply_text(
        'Mandami la tua posizione'
        )
        return LOCATION
    else:
        update.message.reply_text(
            'Formato del mac address sbagliato, per favore riscrivilo'
        )
        return MAC_ADDRESS

def getlocation(update: Update, context: CallbackContext) -> int:
    global latitudine, longitudine
    user_location = update.message.location
    latitudine = user_location.latitude
    longitudine = user_location.longitude
    print(latitudine)
    print(longitudine)
    geolocator = Nominatim(user_agent="Consegna Pacchi")
    location = geolocator.reverse(str(latitudine) + ", " + str(longitudine))
    indirizzo = location.raw['address']['road'] + ', ' + location.raw['address']['house_number']
    print(indirizzo)
    #print(location.address)
    #print(location.raw)
    
    update.message.reply_text(
        'Perfetto, configurazione completata!\n'
        "Quando dovrai ricevere una consegna ma non sei in casa ti verrà invitato qui un messaggio contenente l'indirizzo in cui verrà lasciato il tuo pacco.\n"
        'Verrai anche contattato nel caso un vicino non sia in casa ed il corriere sta per lasciare il pacco da te.\n'
        'A presto!'
    )

    #AGGIUNGERE AL DATABASE 
    cursor = connection.cursor()
    chatId = update.effective_chat.id
    point = "POINT(" + str(latitudine) + " " + str(longitudine) + ")"
    sql =  "INSERT INTO JJ (presenza, nome, cognome, MAC, posizione, indirizzo, chatID) VALUES (%s, %s, %s, %s, ST_GeomFromText(%s, 4326), %s, %s)" 
    cursor.execute(sql, (prova, nome, cognome, mac_address, point, indirizzo, chatId))
    connection.commit()

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    update.message.reply_text(
        'Configurazione annullata'
    )
    return ConversationHandler.END

def reset(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Sei sicuro di voler resettare i tuoi dati? (si/no)\n'
    )
    return RESET

def getresetresponse(update: Update, context: CallbackContext) -> int:
    reset_response = update.message.text
    if (reset_response.lower() == 'si'): 
        print(reset_response)
        cursor = connection.cursor()
        chatId = update.effective_chat.id
        sql = "DELETE FROM JJ WHERE chatID=%s"
        cursor.execute(sql, chatId)
        connection.commit()
        update.message.reply_text(
        'Reset effettuato correttamente!'
        )
        return ConversationHandler.END
    elif (reset_response.lower() == 'no'):
        update.message.reply_text(
            'Ok! Nessun reset effettuato'
        )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            'Devi rispondere si o no'
        )
        return RESET

def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher


    dispatcher.add_handler(CommandHandler("start", start))

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('config', config)],
        states={
            NAME: [MessageHandler(Filters.text, getname)],
            LAST_NAME: [MessageHandler(Filters.text, getlast_name)],
            MAC_ADDRESS: [MessageHandler(Filters.text, getmac)],
            LOCATION: [MessageHandler(Filters.location, getlocation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    conv_handler2 = ConversationHandler(
        entry_points=[CommandHandler('reset', reset)],
        states={
            RESET: [MessageHandler(Filters.text, getresetresponse)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(conv_handler2)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    flask_thread = FlaskThread()
    flask_thread.start()

    main()