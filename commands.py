import telegram
import datetime
from datetime import datetime
import requests

from models import Subscription, Room
from util import with_touched_chat, escape_markdown
from telegram import ParseMode

# for debug mode
DEBUG_MODE = False
USERID_CONTROL = [6128221] # Telegram user with privileges

# max of history records to be stored
MAX_HISTORY = 5

# URL sensorizar UZ
SENSORIZAR_URL="https://sensorizar.unizar.es:8080/api"
# Assests file
ASSETS_FILE="files/assets.csv"

# emojis
SMILEFACE=u'\U0001F643'
FEARFACE=u'\U0001F628'
SKULL=u'\U00002620'

from classes import CLASS_LIST

import random
MASTER_PHRASES = ["Well, this is embarrasing. I only obey my master :_(", "How you dare! I'll tell my boyfriend!", "неподдерживаемая функция"]

def random_string():
    return random.choice(MASTER_PHRASES)


def cmd_ping(bot, update):
    bot.reply(update, 'Pong!')

LEGAL_TEXT="""
TEXTO LEGAL (cumplimiento RGPD y LO 3/2018)

Tus datos recogidos como identificadores mediante el uso de este bot (NIA, DNI, correo electrónico o número de teléfono) y almacenados en el servidor del BOT, se usarán para enviarlos de manera automática a las aulas que indiques. Eventualmente, estos datos pueden ser procesados con fines meramente estadísticos acerca del uso del BOT (datos considerados de legítimo interés para propósitos de investigación científica por el controlador, art. 6(1)(f) GDPR).

Recuerda que estos datos se van a remitir de manera automática al formulario web de la Universidad de Zaragoza disponible en https://eina.unizar.es/asistencia-aula. Por tanto, usando este BOT, estás aceptando que se recojan tus datos de asistencia dentro del marco de las medidas Anti-COVID19.

La recogida de información de asistencia presencial en las aulas de EINA por parte de la Universidad se realiza exclusivamente en el marco de las medidas Anti-Covid19. La información será utilizada exclusivamente en el caso de que resulte necesario localizar contactos con pacientes covid confirmados. A los 14 días toda la información será eliminada.
"""

def cmd_legal(bot, update, chat=None):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

    bot.reply(update, LEGAL_TEXT)
    return

@with_touched_chat
def cmd_start(bot, update, chat=None):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

    bot.reply(
            update, """
¡Hola! 

Este BOT (no oficial) sirve para facilitar la recogida de asistencia a clase en el marco de las medidas Anti-COVID19 en las aulas de la Escuela de Ingeniería y Arquitectura de la Universidad de Zaragoza. Para usarlo, primero tienes que suscribir tu identificador (o identificadores) que quieres utilizar con el comando /sub. El identificador más habitual es tu NIA o NIP. Después, puedes registrar tu asistencia a un aula determinada mediante el comando /assist CODIGO_CLASE. Para saber el código de la clase, puedes consultar /class. Para más información, consulta /help.
""" + LEGAL_TEXT)

@with_touched_chat
def cmd_help(bot, update, chat=None):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return
    bot.reply(update, """
¡Hola! Este bot te permite introducir tu asistencia a clase en la EINA en el marco de las medidas Anti-COVID19 de manera automática

Lista de comandos soportados:
- /sub - subscribir un nuevo identificador (NIA, o cualquier otro dato que permitan tu identificación personal -- DNI, correo electrónico o número de teléfono)
- /unsub - desuscribir un identificador
- /list  - listar los identificadores actuales
- /wipe - eliminar toda tu información (incluidos identificadores definidos) almacenada en el servidor
- /assist - asistir a un aula determinada (realiza la petición al formulario web de la EINA)
- /class - listar los códigos de aulas
- /history - listar tu histórico (5 últimas) de aulas donde has registrado asistencia
- /telemetry - consulta el CO2, temperatura y humedad del aula consultada
- /source - información del código fuente
- /legal - muestra el texto legal (cumplimiento RGPD y LO 3/2018)
- /help - muestra el mensaje de ayuda

Este bot es código abierto (licencia GNU/GPLv3), ¡lee /source para más información!
""",
                  disable_web_page_preview=True,
                  parse_mode=telegram.ParseMode.MARKDOWN)


@with_touched_chat
def cmd_sub(bot, update, args, chat=None):

    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

    if len(args) < 1:
        bot.reply(update, "Uso: /sub identificador1 identificador2 identificador3 ...")
        return
    user_ids = args
    not_found = []
    already_subscribed = []
    successfully_subscribed = []

    for user_id in user_ids:
        if Subscription.select().where(
                Subscription.u_id == user_id,
                Subscription.tg_chat == chat).count() == 1:
            already_subscribed.append(user_id)
            continue

        Subscription.create(tg_chat=chat, u_id=user_id)
        successfully_subscribed.append(user_id)

    reply = ""
    if len(already_subscribed) is not 0:
        reply += "Identificador {} ya definido\n\n".format(
                     ", ".join(already_subscribed)
                 )

    if len(successfully_subscribed) is not 0:

        reply += "Identificador añadido: {}".format(
                     ", ".join(successfully_subscribed)
                 )

    bot.reply(update, reply)


@with_touched_chat
def cmd_unsub(bot, update, args, chat=None):
    
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

    if len(args) < 1:
        bot.reply(update, "Uso: /unsub identificador1 identificador2 identificador3 ...")
        return
    
    user_ids= args
    not_found = []
    successfully_unsubscribed = []

    for user_id in user_ids:
        if Subscription.select().where(
                Subscription.u_id == user_id,
                Subscription.tg_chat == chat).count() == 0:
            not_found.append(user_id)
            continue

        Subscription.delete().where(
            Subscription.u_id == user_id,
            Subscription.tg_chat == chat).execute()

        successfully_unsubscribed.append(user_id)

    reply = ""

    if len(not_found) is not 0:
        reply += "Mmm no encuentro ningún identificador {}\n\n".format(
                     ", ".join(not_found)
                 )

    if len(successfully_unsubscribed) is not 0:
        reply += "Identificador {} eliminado".format(
                     ", ".join(successfully_unsubscribed)
        )

    bot.reply(update, reply)


@with_touched_chat
def cmd_list(bot, update, chat=None):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

    subscriptions = list(Subscription.select().where(
                         Subscription.tg_chat == chat))

    if len(subscriptions) == 0:
        return bot.reply(update, 'No has añadido ningún identificador todavía. Añade un identificador con /sub identificador')

    bot.reply(
        update,
        "Tienes definidos los siguientes identificadores:\n" +
        "\n - ".join((s.u_id for s in subscriptions)) + "\n\nPuedes eliminar cualquiera de ellos con /unsub identificador")


@with_touched_chat
def cmd_wipe(bot, update, chat=None):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

    subscriptions = list(Subscription.select().where(
                         Subscription.tg_chat == chat))

    subs = "Has eliminado todos tus identificadores."
    if subscriptions:
        subs = ''.join([
            "Concretamente, se han eliminado tus siguientes identificadores: ",
            ', '.join((s.u_id for s in subscriptions)),
            '.'])

    bot.reply(update, "De acuerdo, me estoy olvidando de esta conversación. " + subs +
                    " Cuando quieras nos volvemos a ver. Hasta la próxima!")
    chat.delete_instance(recursive=True)

@with_touched_chat
def cmd_history(bot, update, chat=None):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

    # get the history of this user and return it
    _classes = list(Room.select().where(Room.tg_chat == chat).order_by(Room.last_time.desc()))
    bot.reply(update, "Lista de " + str(MAX_HISTORY) + " últimas asistencias registradas:\n" + "\n".join(" - {} ({})".format(_class.last_time.strftime('%a %d %b, %Y, %H:%M'), _class.room_name) for _class in _classes))
    return

@with_touched_chat
def cmd_source(bot, update, chat=None):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

    bot.reply(update, "Este bot es Software Libre bajo licencia GPLv3. "
                        "Código disponible en: "
                        "https://github.com/reverseame/asistencia-aula-EINA-telegram-bot\n"
                        "Adaptado por parte del grupo DisCo de la Universidad de Zaragoza, a partir del código original de: "
                    "https://github.com/franciscod/telegram-twitter-forwarder-bot")

_dict = {} # global var
def loadCSV(filename) -> dict:
    global _dict
    data = read_data(filename)
    _dict = {}
    for line in data:
        line = line.split(',')
        _dict[line[0]] = {'CRE': line[1], 'asset-id': line[2]}
    return _dict

def read_data(file):
    with open(file, 'r') as f:
        return f.read().splitlines()

def getSensorizarPubToken():
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    data = '{"publicId": "4d6266d0-7cc8-11eb-84c3-639131675c2d"}'

    response = requests.post(SENSORIZAR_URL + '/auth/login/public', headers=headers, data=data)

    if response.status_code != 200:
        return None # XXX control this
    else:
        data = response.json()
        return data['token']

def getTelemetry(token: str, asset: str):
    headers = {
        'X-Authorization': "Bearer {}".format(token),
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    params = (
        ('keys', 'co2,temperature,humidity'),
    )

    response = requests.get("{}/plugins/telemetry/ASSET/{}/values/timeseries".format(SENSORIZAR_URL, asset), headers=headers, params=params)
    if response.status_code != 200:
        return None
    else:
        return response.json()

def check_co2_value(value: int) -> str:
    if value < 700:
        return "NORMAL " + SMILEFACE
    elif value < 850:
        return "<b>¡ALTO!</b> " + FEARFACE
    else:
        return "<b>¡MUY ALTO!</b> " + SKULL

def parse_telemetry_message(data):
    co2_value = data['co2'][0]['value']
    temperature = data['temperature'][0]['value']
    humidity = data['humidity'][0]['value']

    if co2_value != None:
        text_co2 = check_co2_value(int(co2_value))
    else:
        text_co2 = SKULL + " SIN DATOS " + SKULL
        
    return "CO2: {} ({})\nTemperatura: {}ºC\nHumedad: {}".format(co2_value, text_co2, temperature, humidity)

def get_telemetry_HTMLmessage(data) -> str:
    return "<i>{}</i>\n{}".format(
                        datetime.now().strftime('%a %d %b, %Y, %H:%M'), 
                        parse_telemetry_message(data))

@with_touched_chat
def cmd_telemetry(bot, update, args, chat=None, already_validated=False):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return
    if len(_dict) == 0: # load CSV, if it has not loaded yet
        loadCSV(ASSETS_FILE)

    if not already_validated:
        _class = valid_args(bot, update, args)
        if _class == None:
            return
    else:
        _class = args
    # if True, we assume _class is *NOT* None

    # if not supported, report the user and ask for future support
    if _dict.get(_class) == None:
        bot.reply(update, "La telemetría de este aula todavía no está soportada :(. Contacta con @RicardoJRdez y hazle llegar el aula que quieres consultar para darle soporte. ¡Gracias!")
        return

    # get public token and telemetry data
    token = getSensorizarPubToken()
    if token is not None:
        telemetry_data = getTelemetry(token, _dict.get(_class)['asset-id'])
        if telemetry_data is not None:
            # parse the data appropriately
            bot.reply(update, get_telemetry_HTMLmessage(telemetry_data), parse_mode=ParseMode.HTML)
        else:
            bot.reply(update, "Ups :(, algo fue mal recuperando la telemetría de {} ...".format(_class))
    else:
        bot.reply(update, "Ups :(, algo fue mal intentando recuperar la telemetría de {} ...".format(_class))
        
    return


import requests
URL = 'https://eina.unizar.es/asistencia-aula?aula='

@with_touched_chat
def cmd_assistmonitor(bot, update, args, chat=None):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

    return


"""
Check validity of args for /assist, /assistmonitor, and /telemetry
and return first argument
"""
def valid_args(bot, update, args):
    if ' ' in args or len(args) <= 0:
        bot.reply(update, "Verifica el aula dada, no debe de ser nula o contener espacios!")
        return None
    elif len(args) > 1:
        bot.reply(update, "Sólo se permite un aula!")
        return None

    return args[0]


@with_touched_chat
def cmd_assist(bot, update, args, chat=None):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

    _class = valid_args(bot, update, args)
    if _class == None:
        return

    subscriptions = list(Subscription.select().where(Subscription.tg_chat == chat))

    if len(subscriptions) == 0:
        bot.reply(update, "Antes de usar este comando, tienes que definir algún identificador!")
        return
   
    # store the class passed as argument, if not repeated
    if Room.select().where(Room.tg_chat == chat).count() >= MAX_HISTORY:
        ordered_rooms = list(Room.select().where(Room.tg_chat == chat).order_by(Room.last_time.asc()))
        # get oldest items, leaving newest (MAX_HISTORY - 1) items
        ordered_rooms = ordered_rooms[0:-(MAX_HISTORY - 1)]
        for _room in ordered_rooms:
            _room.delete_instance() # delete it

    # silently insert the new item into the DB
    Room.create(tg_chat = chat, room_name = _class)

    for subs in subscriptions:
        # create thread to handle the new POST request
        try:
            thread = threading.Thread(target=make_new_POST, args=(bot, update, subs.u_id, _class, ))
            thread.start()
        except:
            bot.reply(update, "Error intentando crear un hilo para la asistencia de \"{}\" :(".format(subs))

import threading
import time
def make_new_POST(bot, update, u_id, _class):
    try:
        # sleep for a random time first
        sleeptime = random.randint(1, 10)
        bot.reply(update, "Durmiendo {} segundos (registro de \"{}\" en \"{}\") ...".format(sleeptime, u_id, _class))
        time.sleep(sleeptime)
        _return = make_request(u_id, _class)
        if not "Gracias por tu colaboración" in _return.text:
            raise Exception("Petición de {} a {} incorrecta!".format(user_id, _class))

        bot.reply(update, "Asistencia de \"{}\" a \"{}\" registrada correctamente".format(u_id, _class))

        # send telemtry message too
        cmd_telemetry(bot, update, _class, already_validated=True)

    except Exception as e:
        bot.reply(update, "ERROR! {0}".format(e.args))

def make_request(user_id, _class):
    # aight, time to go. Build the request now
    payload = {
        "submitted[nip]": user_id,
        "submitted[consentimiento][si]": "si",
        "details[sid]": "",
        "details[page_num]": "1",
        "details[page_count]": "1",
        "details[finished]": "0",
        "form_build_id": "form-_1alOlxKaiBugV4vu8RQ30zR0Qe9JL1zoDO3raHuPK8",
        "form_id": "webform_client_form_3589",
        "op": "Enviar",
    }

    # send and check result, reporting to the user appropriately
    session = requests.session()
    request = session.post(URL + _class, data=payload)
    
    if not request.ok:
        raise Exception("Petición de {} a {} ha devuelto error (código de error {})".format(user_id, _class, request.status_code))
    
    return request
    

@with_touched_chat
def cmd_class(bot, update, chat=None):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return
    bot.reply(update, "Lista (no exhaustiva) de código de aulas:\n" +  CLASS_LIST + 
                        "\nSi el aula donde vas a asistir no está en esta lista, para conocerla puedes escanear el QR de la puerta y observar el enlace que contiene. El código del aula aparece al final de la URL (parámetro \"aula\")\n\nEl formato de las aulas parece seguir el esquema: <CC><P><aula>, donde <CC> es la abreviatura del edificio (AB, TQ, BT), <P> planta, y <aula> el número de aula")

@with_touched_chat
def handle_chat(bot, update, chat=None):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

