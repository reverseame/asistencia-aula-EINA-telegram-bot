# Asistencia-Aula-EINA-Telegram-bot 

Bot para Telegram que facilita la recogida de asistencia a clase en el marco de las medidas Anti-COVID19 en las aulas de la [Escuela de Ingeniería y Arquitectura](https://eina.unizar.es) de la [Universidad de Zaragoza](https://www.unizar.es).

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

### ¿Puedo usarlo ya?

Sí, sólo tienes que buscar a [@AsistenciaAulaEINA_bot](http://t.me/AsistenciaAulaEINA_bot) en Telegram y empezar a conversar con él. Iniciar esta conversación supone que aceptas las [condiciones legales respecto a la recogida de datos](#texto-legal).

Después:
1. Suscribe tu identificador (o identificadores) que quieres utilizar con el comando `/sub`. El identificador más habitual es tu NIA o NIP.
2. Registra tu asistencia a un aula determinada mediante el comando `/assist CODIGO_CLASE`. Para saber el código de la clase, puedes consultar `/class` o escanear el QR de las puertas del aula de interés y observar lo que aparece al final de la URL (antecedido por `aula=`).
3. Automáticamente, el bot registrará todos los identificadores definidos de tu usuario en el aula indicada a través del formulario de la EINA habilitado a tal efecto en [https://eina.unizar.es/asistencia-aula](https://eina.unizar.es/asistencia-aula). Para cada identificador esperará unos segundos y realizará la petición, informándote del resultado.

Para más información de los comandos disponibles, consulta `/help`.

Para sacar el máximo provecho de este bot, puedes dejar mensajes programados a tus horas de inicio de clases presenciales en la conversación de Telegram.

## Requisitos

- Python 3.5 (probado con Python 3.5.3 sobre Debian GNU/Linux bullseye/sid 8.11)

## Créditos

Este bot está basado en el trabajo previo de:
- [telegram-twitter-forwarder-bot](https://github.com/franciscod/telegram-twitter-forwarder-bot)

## Despliegue del bot

1. Clona el repositorio
2. Rellena el fichero "secret.env" (explicado más abajo)
3. Crea tu propio entorno virtual y actívalo:
    ```
    virtualenv -p python3.5 venv
    . venv/bin/activate
    . secrets.env
    ```
4. `pip3.5 install -r requirements.txt`
5. Ejecuta `python3.5 main.py`

## Fichero secret.env

Para desplegar un bot en Telegram necesitas tener primero un Telegram Bot Token. Puedes conseguirlo mediante BotFather ([información detallada aquí](https://core.telegram.org/bots)).

Una vez tengas tu token, crea un fichero de nombre `secret.env` con el siguiente contenido:

```
export TELEGRAM_BOT_TOKEN=PEGA_TU_TOKEN_AQUI
```

## Ejecución mediante cron

Añade la siguiente línea en tu fichero `crontab`:
```
* * * * * user cd /home/user/path/to/asistencia-aula-EINA-telegram-bot && ./cron-run.sh >> /dev/null 2>&1
```

Puedes configurar el tiempo de ejecución como quieras.

## Texto legal

(texto legal en cumplimiento del RGPD y de la LO 3/2018)

Tus datos recogidos como identificadores mediante el uso de este bot (NIA, DNI, correo electrónico o número de teléfono) y almacenados en el servidor del BOT, se usarán para enviarlos de manera automática a las aulas que indiques. Eventualmente, estos datos pueden ser procesados con fines meramente estadísticos acerca del uso del BOT (datos considerados de legítimo interés para propósitos de investigación científica por el controlador, art. 6(1)(f) GDPR).

Recuerda que estos datos se van a remitir de manera automática al formulario web de la Universidad de Zaragoza disponible en [https://eina.unizar.es/asistencia-aula](https://eina.unizar.es/asistencia-aula). Por tanto, usando este BOT, estás aceptando que se recojan tus datos de asistencia dentro del marco de las medidas Anti-COVID19.

La recogida de información de asistencia presencial en las aulas de EINA por parte de la Universidad se realiza exclusivamente en el marco de las medidas Anti-Covid19. La información será utilizada exclusivamente en el caso de que resulte necesario localizar contactos con pacientes covid confirmados. A los 14 días toda la información será eliminada.

## Licencia

Código fuente liberado bajo licencia [GNU GPLv3](LICENSE).
