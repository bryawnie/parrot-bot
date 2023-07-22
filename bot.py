from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

from sqlite3 import connect
from hashlib import sha3_256
from datetime import datetime
from random import random

def create_file(filename):
    with open(filename, 'w') as f:
        f.close()

class DatabaseInterface:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def db_query(self, query):
        con = connect(self.db_path)
        cur = con.cursor()
        cur.execute(query)
        con.commit()
        con.close()
    
    def init_database(self):
        """Creates a SQLite database and a table to save phrases"""
        create_file(self.db_path)
        self.db_query("CREATE TABLE phrases (chat_id, hash, author, phrase, added_at)")
    
    def save_phrase(self, **kwargs):
        """Saves a phrase into database"""
        chat_id = kwargs.get('chat_id')
        author = kwargs.get('author').strip()
        message = kwargs.get('message')

        # Sanitize message
        message = message.replace("'", '')
        message = message.replace('"', '')
        message = message.strip()

        # Hash
        tag = sha3_256(message.encode()).hexdigest()

        self.db_query(f"INSERT INTO phrases (chat_id, hash, author, phrase, added_at) VALUES ({chat_id}, '{tag}', '{author}', '{phrase}', '{datetime.now()}')")

    def delete_phrase(self, tag):
        """Deletes from database the phrase with matching tag"""
        self.db_query(f"DELETE FROM phrases WHERE hash LIKE {tag}*")

    def get_random_phrase_for_chat(self, chat_id):
        con = connect(self.db_path)
        cur = con.cursor()
        try:
            phrase = cur.execute(f"SELECT phrase FROM phrases WHERE chat_id={chat_id} ORDER BY RANDOM() LIMIT 1").fetchone()
            con.close()
            return phrase[0]
        except:
            con.close()
            return "No me entrenaron para esto :c"



class ParrotBot:
    def __init__(self, db_path):
        self.db_interface = DatabaseInterface(db_path)
        self.do_not_bother = []
        self.sensibility = 0.1

    def save_phrase_from_message(self, message):
        try:
            chat_id = message.chat_id
            content = message.text
            author = message.from_user.first_name
            self.db_interface.save_phrase(
                chat_id=chat_id,
                message=content,
                author=author,
            )
        except Exception as e:
            print(f"Error processing message from {author}:") 
            print(e)


    def start(self, update: Update, context: CallbackContext):
        """
            This function is called when the user sends the command /start.
            It sends a welcome message to the user.
        """    
        user = update.message.from_user
        update.message.reply_text(
            f"Hola {user.first_name}!\n" +
            "Soy un bot que sólo sabe repetir cosas que alguien más dijo en este mismo " +
            "chat pero de forma random y sin contexto alguno."
        )


    def remove_phrase(self, update: Update, context: CallbackContext):
        """Removes a phrase from the phrases table given its hash."""
        try:
            [ _, phrase_id ] = update.message.text.split(' ')
            self.db_interface.delete_phrase(phrase_id)
            update.message.reply_text("Se ha eliminado la frase.")
        except:
            update.message.reply_text("Hubo un error procesando tu mensaje, por favor intenta de nuevo: /remove <id_frase>")


    def silence(self, update: Update, context: CallbackContext):
        """Silences the bot in current chat"""
        chat_id = update.message.chat_id
        if chat_id in self.do_not_bother:
            update.message.reply_text("Pero si ya estoy calladito :c")
        else:
            self.do_not_bother.append(chat_id)
            update.message.reply_text("Okidoki, calladín bombín!")


    def activate(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        if chat_id in self.do_not_bother:
            self.do_not_bother.remove(chat_id)
        else:
            update.message.reply_text("Voy a cucharear en conversaciones a lo sapo :)")


    def ping(self, update: Update, context: CallbackContext):
        """Testing command"""
        update.message.reply_text("pong")


    def default(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        message = update.message.text

        if chat_id in self.do_not_bother:
            return

        # Response conditions
        if random() < self.sensibility or "kebin" in message.lower():
            response = self.db_interface.get_random_phrase_for_chat(chat_id)
            update.message.reply_text(response)
        
        # Save conditions
        # WIP
        # update.message.reply_text(content, parse_mode='Markdown')


def runner(token: str):
    updater = Updater(token, use_context=True)
    parrot_bot = ParrotBot(db_path='db.sqlite')
    
    updater.dispatcher.add_handler(CommandHandler('start', parrot_bot.start))
    updater.dispatcher.add_handler(CommandHandler('remove', parrot_bot.remove_phrase))
    updater.dispatcher.add_handler(CommandHandler('silence', parrot_bot.silence))
    updater.dispatcher.add_handler(CommandHandler('activate', parrot_bot.activate))
    updater.dispatcher.add_handler(CommandHandler('ping', parrot_bot.ping))

    updater.dispatcher.add_handler(MessageHandler(Filters.text, parrot_bot.default))
    #updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()
