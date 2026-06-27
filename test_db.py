import sqlite3

def check_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(user)")
    cols = [info[1] for info in cursor.fetchall()]
    print("Columns in user table:", cols)
    conn.close()

if __name__ == "__main__":
    check_db()
