import telegram
import datetime
from datetime import datetime, timedelta
import requests

from models import Subscription, Room
from util import with_touched_chat, escape_markdown
from telegram import ParseMode

# for debug mode
DEBUG_MODE = False
USERID_CONTROL = [6128221] # Telegram user with privileges

# max of history records to be stored
MAX_HISTORY = 5
DEFAULT_TIME = 50 # in minutes

# URL sensorizar UZ
SENSORIZAR_URL="https://sensorizar.unizar.es:8080/api"
# Assests file
ASSETS_FILE="files/assets.csv"

# emojis
SMILEFACE=u'\U0001F643'
FEARFACE=u'\U0001F628'
SKULL=u'\U00002620'
SCHOOL=u'\U0001F3EB'
from classes import CLASS_LIST

import random
MASTER_PHRASES = ["Well, this is embarrasing. I only obey my master :_(", "How you dare! I'll tell my boyfriend!", "неподдерживаемая функция"]

def random_string():
    return random.choice(MASTER_PHRASES)


def cmd_ping(bot, update):
    bot.reply(update, 'Pong!')

HELP_TEXT="""¡Hola! Este bot te permite introducir tu asistencia a clase en la EINA en el marco de las medidas Anti-COVID19 de manera automática

Lista de comandos soportados:
- /sub ID - subscribir un nuevo identificador ID (NIA, o cualquier otro dato que permitan tu identificación personal -- DNI, correo electrónico o número de teléfono). Sólo se permite un ID por usuario. Cada llamada a este comando sustituye el identificador anterior
- /unsub - desuscribir el identificador asociado a tu usuario 
- /list  - listar tu ID actual
- /wipe - eliminar toda tu información (incluidos identificadores definidos) almacenada en el servidor
- /assist AULA [TIEMPO] - asistir a una AULA determinada durante TIEMPO minutos (realiza la petición al formulario web de la EINA cada {0} minutos, si TIEMPO >= {0}). Valor por defecto TIEMPO={0}
- /class - listar los códigos de aulas
- /history - listar tu histórico (5 últimas) de aulas donde has registrado asistencia
- /telemetry AULA [TIEMPO] - consulta el CO2, temperatura y humedad de la AULA consultada durante TIEMPO minutos. Si TIEMPO<0, finaliza la monitorización continua. Valor por defecto TIEMPO={0}
- /source - información del código fuente
- /legal - muestra el texto legal (cumplimiento RGPD y LO 3/2018)
- /help - muestra el mensaje de ayuda

Este bot es código abierto (licencia GNU/GPLv3), ¡lee /source para más información!
""".format(DEFAULT_TIME)

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

Este BOT (no oficial) sirve para facilitar la recogida de asistencia a clase en el marco de las medidas Anti-COVID19 en las aulas de la Escuela de Ingeniería y Arquitectura de la Universidad de Zaragoza. Para usarlo, primero tienes que suscribir el identificador que quieres utilizar con el comando /sub. El identificador más habitual es tu NIA o NIP. Después, puedes registrar tu asistencia a un aula determinada mediante el comando /assist CODIGO_CLASE. Este comando permite un parámetro adicional para indicar durante cuánto tiempo quieres registrar tu asistencia. Por defecto, cada 50 minutos tras mandar el comando "/assist" registrará de forma automática tu asistencia. Para saber el código de la clase, puedes consultar /class. Para más información, consulta /help.
""" + LEGAL_TEXT)

@with_touched_chat
def cmd_help(bot, update, chat=None):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return
    bot.reply(update, HELP_TEXT,
                  disable_web_page_preview=True,
                  parse_mode=telegram.ParseMode.MARKDOWN)

def delete_subscription(chat):
    try:
        query = Subscription.get(Subscription.tg_chat == chat)
        if query is not None:
            query.delete_instance()
            return query.u_id

    except Subscription.DoesNotExist:
        return None

@with_touched_chat
def cmd_sub(bot, update, args, chat=None):

    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

    if len(args) < 1 or len(args) > 1:
        bot.reply(update, "Uso: /sub identificador ...")
        return
    user_id = args[0]

    already_subscribed = delete_subscription(chat)
    Subscription.create(tg_chat=chat, u_id=user_id)

    reply = ""
    if already_subscribed is not None:
        reply += "Identificador eliminado: {}\n\n".format(already_subscribed)

    reply += "Identificador añadido: {}".format(user_id)

    bot.reply(update, reply)
    return

@with_touched_chat
def cmd_unsub(bot, update, chat=None):
    
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

    u_id = delete_subscription(chat)
    reply = ""
    if u_id is None:
        reply += "Mmm no encuentro ningún identificador definido para tu usuario :/"
    else:
        reply += "Identificador {} eliminado".format(u_id)

    bot.reply(update, reply)
    return

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
        "Tienes definido el siguiente identificador:\n" +
        "\n - ".join((s.u_id for s in subscriptions)) + "\n\nPuedes eliminarlo con /unsub o sustituirlo con /sub nuevo_identificador")


@with_touched_chat
def cmd_wipe(bot, update, chat=None):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

    subscriptions = list(Subscription.select().where(
                         Subscription.tg_chat == chat))

    subs = "Has eliminado tu identificador."
    if subscriptions:
        subs = ''.join([
            "Concretamente, se ha eliminado tu identificador: ",
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
    bot.reply(update, "Lista de " + str(MAX_HISTORY) + " últimas asistencias registradas:\n" + "\n".join(" - {} ({}{})".format(_class.last_time.strftime('%a %d %b, %Y, %H:%M'), _class.room_name, " " + SCHOOL if  _class.still_in_room else "") for _class in _classes))
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
        _class, _time = valid_args(bot, update, args)
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
"""
Check validity of args for /assist and /telemetry
and return first argument (mandatory) and second argument (optional)
"""
def valid_args(bot, update, args):
    if len(args) <= 0:
        bot.reply(update, "Verifica el aula dada, no debe de ser nula!")
        return None, None
    elif len(args) > 2:
        bot.reply(update, "Este comando sólo recibe dos parámetros: AULA [TIEMPO]")
        return None, None
    elif len(args) == 1:
        return args[0], DEFAULT_TIME

    return args[0], int(args[1])


@with_touched_chat
def cmd_assist(bot, update, args, chat=None):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

    _class, _time = valid_args(bot, update, args)
    if _class == None:
        return

    subscriptions = list(Subscription.select().where(Subscription.tg_chat == chat))

    if len(subscriptions) == 0:
        bot.reply(update, "Antes de usar este comando, tienes que definir algún identificador!")
        return
   
    # check if we need to stop assistance thread, if any
    if _time < 0:
        try:
            query = list(Room.select().where(Room.tg_chat == chat, Room.room_name == _class).order_by(Room.last_time.desc()))
            query[0].still_in_room = False
            query[0].save()
            _str =  "Registro automático de asistencia en clase {} finalizado".format(_class)
        except:
            _str = "Vaya! No he encontrado ninguna clase {} con asistencia previa registrada :(".format(_class)
        
        bot.reply(update, _str)
        return
    
    ordered_rooms = list(Room.select().where(Room.tg_chat == chat, Room.room_name == _class).order_by(Room.last_time.asc()))
    # check if the user is already in the _class
    if len(ordered_rooms) >= 1:
        last_room = ordered_rooms[-1]
        next_ts = last_room.last_time + timedelta(minutes=DEFAULT_TIME)
        present_ts = datetime.now()
        if present_ts < next_ts:
            # cannot assist more than once to _class in < DEFAULT_TIME!
            bot.reply(update, "Vaya! No puedes registrar la asistencia al mismo aula en menos de {} minutos! Podrás hacerlo a las {}".format(DEFAULT_TIME, next_ts.strftime("%H:%M:%S")))
            return

    # check if we need to delete the oldest room 
    ordered_rooms = list(Room.select().where(Room.tg_chat == chat).order_by(Room.last_time.asc()))
    if len(ordered_rooms) >= MAX_HISTORY:
        # get oldest items, leaving newest (MAX_HISTORY - 1) items
        ordered_rooms = ordered_rooms[0:-(MAX_HISTORY - 1)]
        for _room in ordered_rooms:
            _room.delete_instance() # delete it

    # silently insert the new item into the DB
    new_room = Room.create(tg_chat = chat, room_name = _class)
    for subs in subscriptions:
        # create thread to handle the new POST request
        try:
            thread = threading.Thread(target=register_assistance, args=(bot, update, new_room.id, subs.u_id, _class, _time))
            thread.start()
        except:
            bot.reply(update, "Error intentando crear un hilo para la asistencia de \"{}\" :(".format(subs))

import threading
import time
def register_assistance(bot, update, room_id, u_id, _class, _time):
    still_in_room = True
    room = None
    end_ts = datetime.now() + timedelta(minutes=_time)
    while still_in_room and (abs(datetime.now() - end_ts) > timedelta(seconds=1)):
        next_ts = datetime.now() + timedelta(minutes=DEFAULT_TIME)
        make_new_POST(bot, update, u_id, _class)
        if (abs(end_ts - next_ts) >= timedelta(minutes=DEFAULT_TIME)):
            bot.reply(update, "Próximo registro a las {} ...".format(next_ts.strftime("%H:%M")))
            time.sleep(DEFAULT_TIME*60) # sleep in seconds
        else:
            end_ts = datetime.now()

        room = Room.get(Room.id == room_id)
        still_in_room = room.still_in_room
        
    if still_in_room:
        # update the still_in_room field
        room.still_in_room = False
        room.save()
        bot.reply(update, "Registro periódico de asistencia a clase {} finalizado".format(_class))
    
    return

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

