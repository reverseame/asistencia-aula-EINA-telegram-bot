#!/bin/sh
if [ `pgrep -f asistencia-aula-telegram-bot.py` ];
then
    echo "Already running"
    exit 1
else
    . venv/bin/activate
    . ./secrets.env
    python3.5 asistencia-aula-telegram-bot.py
    exit 0
fi
