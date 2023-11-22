import sqlite3
from sqlite3 import Error

db_file = "securiSense.db"
conn = sqlite3.connect(db_file)
cur = conn.cursor()


def create_user(user):
    sql = '''INSERT INTO users (username, password, email, address, phone_number)
             VALUES(?,?,?,?,?)'''
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


def getUsers(conn, cur):
    users = cur.execute("""SELECT * FROM users""")
    return users
