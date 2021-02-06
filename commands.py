import telegram

from models import Subscription
from util import with_touched_chat, escape_markdown

DEBUG_MODE = True
USERID_CONTROL = [6128221]

import random
MASTER_PHRASES = ["Well, this is embarrasing. I only obey my master :_(", "How you dare! I'll tell my boyfriend!", "неподдерживаемая функция"]

def random_string():
    return random.choice(MASTER_PHRASES)


def cmd_ping(bot, update):
    bot.reply(update, 'Pong!')


@with_touched_chat
def cmd_start(bot, update, chat=None):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

    bot.reply(
            update, """
Hola! 

Este BOT sirve para poder facilitar la recogida de asistencia a clase en el marco de las medidas Anti-COVID19 en las aulas de la Escuela de Ingeniería y Arquitectura de la Universidad de Zaragoza. Tus datos recogidos como identificadores mediante el uso de este bot (NIA, DNI, correo electrónico o número de teléfono) y almacenados en el servidor del BOT, se usarán para enviarlos de manera automática a las aulas que indiques. Eventualmente, estos datos pueden ser procesados con fines meramente estadísticos acerca del uso del BOT (datos considerados de legítimo interés para propósitos de investigación científica por el controlador, art. 6(1)(f) GDPR).

Recuerda que estos datos se van a remitir de manera automática al formulario web de la Universidad de Zaragoza disponible en https://eina.unizar.es/asistencia-aula. Por tanto, usando este BOT, estás aceptando que se recojan tu datos de asistencia dentro del marco de las medidas Anti-COVID19.

La recogida de información de asistencia presencial en las aulas de EINA por parte de la Universidad se realiza exclusivamente en el marco de las medidas Anti-Covid19. La información será utilizada exlusivamente en el caso de que resulte necesario localizar contactos con pacientes covid confirmados. A los 14 días toda la información será eliminada.

""")

@with_touched_chat
def cmd_help(bot, update, chat=None):
    #import pdb; pdb.set_trace();
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return
    bot.reply(update, """
Hola! Este bot te permite introducir tu asistencia a clase en la EINA en el marco de las medidas Anti-COVID19 de manera automática

Lista de comandos soportados:
- /sub - subscribir un nuevo identificador (NIA, o cualquier otro dato que permitan tu identificación personal -- DNI, correo electrónico o número de teléfono)
- /unsub - de-suscribir un identificador
- /list  - listar los identificadores actuales
- /wipe - elimina toda tu información (incluidos identificadores definidos) almacenada en el servidor
- /source - información del código fuente
- /help - muestra el mensaje de ayuda

Este bot es código abierto (licencia GNU/GPLv3), lee /source para más información!
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

    subs = ['']
    for sub in subscriptions:
        subs.append(sub.u_id)

    bot.reply(
        update,
        "Tienes definidos los siguientes identificadores:\n" +
        "\n - ".join(subs) + "\n\nPuedes eliminar cualquiera de ellos con /unsub identificador")


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
def cmd_source(bot, update, chat=None):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

    bot.reply(update, "Este bot es Software Libre bajo licencia GPLv3. "
                        "Código disponible en: "
                        "https://github.com/reverseame/asistencia-aula-EINA-telegram-bot\n"
                        "Adaptado por parte del grupo DisCo de la Universidad de Zaragoza, a partir del código original de:"
                    "https://github.com/franciscod/telegram-twitter-forwarder-bot")


@with_touched_chat
def handle_chat(bot, update, chat=None):
    if DEBUG_MODE:
        if (chat.chat_id not in USERID_CONTROL):
            bot.reply(update, random_string())
            return

