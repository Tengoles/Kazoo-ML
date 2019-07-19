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

MACS = ['5c:70:a3:0e:28:b2', '04:d6:aa:69:da:f1']     #estas serian las MACs usadas para entrenar el modelo

test_times = [[('20190411-115300', '20190411-120000')], [('20190411-120400','20190411-121200')],
                  [('20190411-121400', '20190411-122300')], [('20190411-125700','20190411-130700')]]  # rangos de tiempo en los que se realizo cada entrenamiento, uno por cada clase

train_data_path = "/home/ubuntu/Kazoo-ML/flaskr/train_data/"

predict_data_path = "/home/ubuntu/Kazoo-ML/flaskr/predict_data/"

LOG_FILE=  "/home/ubuntu/Kazoo-ML/flaskr/logs/messages.log"

engine_string = 'postgresql://user:passwd@localhost:5432/db_name'

HUBS = get_hubs()

notification_mail = "enzo.tng@gmail.com"
