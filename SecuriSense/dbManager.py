import sqlite3
from sqlite3 import Error

db_file = "securiSense.db"
conn = sqlite3.connect(db_file)
cur = conn.cursor()


def create_user(user, conn, cur):
    sql = '''INSERT INTO users (username, password, email, address, phone_number, salt)
             VALUES(?,?,?,?,?,?)'''
    cur.execute(sql, user)
    conn.commit()
    return cur.lastrowid


def create_alert(alert, conn, cur):
    sql = '''INSERT INTO alerts (location, image, time)
             VALUES(?,?,?)'''
    cur.execute(sql, alert)
    conn.commit()
    print(f"Alert Has been created successfully: {alert[0]} ")
    return cur.lastrowid


def getAlerts(conn, cur):
    alerts = cur.execute("""SELECT * FROM alerts""")
    return alerts

def getAlertsInReverse(conn,cur):
    alerts = cur.execute("""SELECT * FROM alerts ORDER BY time DESC""")
    return alerts

def deleteAllAlerts(conn,cur):
    cur.execute("""DELETE FROM alerts""")
    deleted_rows = cur.rowcount
    conn.commit()
    print(f"{deleted_rows} alerts have been deleted.")
    return f"{deleted_rows} alerts have been deleted."

def getUsers(username, conn, cur):
    query = "SELECT * FROM users WHERE username = ?"
    cur.execute(query, (username,))
    return cur.fetchone()

