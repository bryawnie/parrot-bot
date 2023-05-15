from sqlite3 import connect
from bot import runner
from dotenv import load_dotenv
from os import environ

load_dotenv()

def init(db_name='db.sqlite'):
    with open(db_name, 'w') as db:
        db.close()

    con = connect("db.sqlite")
    cur = con.cursor()

    cur.execute("CREATE TABLE phrases (hash, author, phrase, added_by, added_at)")
    con.commit()

def run_bot():
    runner(token=environ.get('BOT_TOKEN'))
