import sqlite3
from sqlite3 import Error


def create_table(conn, create_table_sql):
    """ Create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_user(conn, user):
    sql = '''INSERT INTO users (username, password, email, address, phone_number)
             VALUES(?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, user)
    conn.commit()
    return cur.lastrowid


def create_alert(conn, alert):
    sql = '''INSERT INTO alerts (location, image, time, status)
             VALUES(?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, alert)
    conn.commit()
    return cur.lastrowid


if __name__ == '__main__':
    db_file = "finalProject.db"  # Add the file extension
    userTableSQL = ("CREATE TABLE IF NOT EXISTS users \
                    (id integer PRIMARY KEY, \
                     username text NOT NULL, \
                     password text NOT NULL, \
                     email text NOT NULL, \
                     address text, \
                     phone_number text);")

    alertTableSQL = ("CREATE TABLE IF NOT EXISTS alerts ( \
                        id integer PRIMARY KEY, \
                        location text NOT NULL, \
                        image text, \
                        time datetime NOT NULL);")

    conn = None
    user = ('example_user', 'hashed_password', 'user@example.com', '123 Main St', '123-456-7890')
    alert = ('Alert Location', 'image_url.jpg', '2023-10-26 14:30:00','ACTIVE')

    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        create_table(conn, userTableSQL)
        print("Created user table")
        create_table(conn, alertTableSQL)
        print("Created alert table")
        create_user(conn, user)
        print("User created")
        create_alert(conn, alert)
        print("Alert created")
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
