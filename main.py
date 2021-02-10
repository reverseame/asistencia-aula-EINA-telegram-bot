import logging
import random

from envparse import Env
from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.ext.messagehandler import MessageHandler, Filters

from bot import AsistenciaAulaEINABot
from commands import *

env = Env(
    TELEGRAM_BOT_TOKEN=str,
)


if __name__ == '__main__':
    random.seed()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.WARNING)

    logging.getLogger(AsistenciaAulaEINABot.__name__).setLevel(logging.DEBUG)

    # initialize telegram API
    token = env('TELEGRAM_BOT_TOKEN')
    updater = Updater(bot=AsistenciaAulaEINABot(token))
    dispatcher = updater.dispatcher

    # set commands
    dispatcher.add_handler(CommandHandler('start', cmd_start))
    dispatcher.add_handler(CommandHandler('help', cmd_help))
    dispatcher.add_handler(CommandHandler('ping', cmd_ping))
    dispatcher.add_handler(CommandHandler('sub', cmd_sub, pass_args=True))
    dispatcher.add_handler(CommandHandler('unsub', cmd_unsub, pass_args=True))
    dispatcher.add_handler(CommandHandler('list', cmd_list))
    dispatcher.add_handler(CommandHandler('wipe', cmd_wipe))
    dispatcher.add_handler(CommandHandler('assist', cmd_assist, pass_args=True))
    dispatcher.add_handler(CommandHandler('class', cmd_class))
    dispatcher.add_handler(CommandHandler('history', cmd_history))
    dispatcher.add_handler(CommandHandler('legal', cmd_legal))
    dispatcher.add_handler(CommandHandler('source', cmd_source))
    dispatcher.add_handler(MessageHandler([Filters.text], handle_chat))

    # poll
    updater.start_polling()
