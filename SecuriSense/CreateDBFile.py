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


if __name__ == '__main__':
    db_file = "securiSense.db"
    userTableSQL = ("CREATE TABLE IF NOT EXISTS users \
                    (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                     username text NOT NULL, \
                     password text NOT NULL, \
                     email text NOT NULL, \
                     address text, \
                     phone_number text);")

    alertTableSQL = ("CREATE TABLE IF NOT EXISTS alerts ( \
                        id integer PRIMARY KEY AUTOINCREMENT NOT NULL, \
                        location text NOT NULL, \
                        image BLOB, \
                        time datetime NOT NULL);")

    conn = None

    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        create_table(conn, userTableSQL)
        print("Created user table")
        create_table(conn, alertTableSQL)
        print("Created alert table")
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()