import datetime
import psycopg2
import pickle


'''
Connect to Postgres database
Insert in table "coords_cache" values
'''
def save_db_cache(dictionaries: dict):    

    conn = None
    try:         
     
        conn = psycopg2.connect(database="postgres", user="postgres", password="postgres", host="localhost", port="5432")
        cur = conn.cursor()
        insert_query = "INSERT INTO coords_cache (id, value, time_stamp) VALUES (%s, %s, %s)"
        cur.execute(insert_query, (1, pickle.dumps(dictionaries), datetime.datetime.now()))   
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def read_db_cache():

    rest = {}

    conn = None
    try:       
        conn = psycopg2.connect(database="postgres", user="postgres", password="postgres", host="localhost", port="5432")
        cur = conn.cursor()
        select_query = "SELECT * FROM coords_cache WHERE id = 1"
        cur.execute(select_query)
        rows = cur.fetchall()

        for row in rows:
            rest = pickle.loads(row[1]) 

       
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            return rest


if __name__ == '__main__':
    #save_db_cache()
    var = read_db_cache()
    print(type(var))