from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

from sqlite3 import connect
from hashlib import sha3_256
from datetime import datetime

DB_FILENAME = 'db.sqlite'


def start(update: Update, context: CallbackContext):
    """
        This function is called when the user sends the command /start.
        It sends a welcome message to the user.
    """    
    user = update.message.from_user
    update.message.reply_text(
        f"""
        Hola {user.first_name}!
        Presiona /comandos para ver la lista de comandos disponibles.
        """
    )


def add_phrase(update: Update, context: CallbackContext):
    """
        Adds a phrase to the phrases table.
    """
    con = connect(DB_FILENAME)
    cur = con.cursor()
    user = update.message.from_user

    try:
        message_text = update.message.text
        message_text = message_text.replace("'", '')
        [ phrase, author ] = update.message.text.split('-')
        phrase = phrase.strip()
        author = author.strip()

        tag = sha3_256(phrase.encode()).hexdigest()

        cur.execute(f"INSERT INTO likes VALUES ({tag}, '{author}', '{phrase}', '{user.id}, {datetime.now()})")
        con.commit()
        con.close()

        update.message.reply_text(
            f"""
            Se ha agregado la frase:
            {phrase} - **{author}**
            Id: `{tag}`
            """
        )
    except:
        update.message.reply_text("Hubo un error procesando tu mensaje, por favor intenta de nuevo: /add <frase> - <autor>")


def my_phrases(update: Update, context: CallbackContext):
    """
        Lists all the phrases created by the user.
    """
    con = connect(DB_FILENAME)
    cur = con.cursor()
    user = update.message.from_user

    try:
        phrases = cur.execute(f"SELECT * FROM phrases WHERE added_by={user.id}").fetchall()
        con.close()
        if len(phrases) == 0:
            update.message.reply_text("No has agregado ninguna frase aún.")
        else:
            update.message.reply_text("Estas son tus frases:\n\n" + '\n'.join([f"`{phrase[0][:8]}`: {phrase[1]} - **{phrase[2]}**" for phrase in phrases]))
    except:
        update.message.reply_text("Hubo un error procesando tu mensaje, por favor intenta de nuevo: /list")


def remove_phrase(update: Update, context: CallbackContext):
    """
        Removes a phrase from the phrases table given its id (hash).
    """
    con = connect(DB_FILENAME)
    cur = con.cursor()
    user = update.message.from_user

    try:
        [ _, phrase_id ] = update.message.text.split(' ')
        cur.execute(f"DELETE FROM phrases WHERE added_by={user.id} AND hash LIKE {phrase_id}*")
        con.commit()
        con.close()
        update.message.reply_text("Se ha eliminado la frase.")
    except:
        update.message.reply_text("Hubo un error procesando tu mensaje, por favor intenta de nuevo: /remove <id_frase>")


def ping(update: Update, context: CallbackContext):
    update.message.reply_text("pong")


def unknown(update: Update, context: CallbackContext):
    update.message.reply_text("chuata")
    pass


def runner(token: str):
    updater = Updater(token, use_context=True)
    
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('add', add_phrase))
    updater.dispatcher.add_handler(CommandHandler('list', list_phrases))
    updater.dispatcher.add_handler(CommandHandler('remove', remove_phrase))

    updater.dispatcher.add_handler(CommandHandler('ping', ping))

    updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
    #updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()