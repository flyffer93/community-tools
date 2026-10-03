import sqlite3
from database import get_connection

def verify_login(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM Staff WHERE username=? AND password=?", (username, password))
    staff = c.fetchone()
    conn.close()
    return staff is not None

def register_staff(username, password):
    conn = get_connection()
    c = conn.cursor()
    try:
        
        c.execute("INSERT INTO Staff (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success