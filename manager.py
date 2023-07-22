from sqlite3 import connect
from bot import runner
from dotenv import load_dotenv
from os import environ, path

load_dotenv()
DB_PATH = "db.sqlite"

def create_file(filename):
    with open(filename, 'w') as f:
        f.close()

def init_database(db_path: str):
    create_file(db_path)

    con = connect(db_path)
    cur = con.cursor()

    # We will restrict the shared content to only conversations
    # with same chat id (or group id)
    cur.execute("CREATE TABLE phrases (chat_id, hash, author, phrase, added_at)")
    con.commit()

def run_bot():
    runner(token=environ.get('BOT_TOKEN'))

if __name__ == '__main__':
    if not path.exists(DB_PATH):
        init_database(DB_PATH)
    run_bot()
