import os
import psycopg2

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host="34.196.210.24", database="kazoo", user="kazoo",
                                password="production.K4zoo2018*")

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # close the communication with the PostgreSQL
        #cur.close()
        return cur, conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def get_hubs():
    cur, conn = connect()
    query = """SELECT * FROM public.hubs_ml"""
    cur.execute(query)
    hubs = cur.fetchall()
    return hubs

predict_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "predict_data")
train_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "train_data")
engine_string = 'postgresql://user:passwd@localhost:5432/db_name'
notification_mails = ["enzo.tng@gmail.com"]