from sqlite3 import connect

def init(db_name='db.sqlite'):
    with open(db_name, 'w') as db:
        db.close()

    con = connect("db.sqlite")
    cur = con.cursor()

    cur.execute("CREATE TABLE phrases (author, phrase, added_by, added_at)")
    con.commit()