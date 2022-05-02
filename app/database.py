import psycopg2
import pickle

'''
Connection to postgres database
Know if a table is empty
'''
def is_table_empty(table_name):
    conn = None
    try:       
        conn = psycopg2.connect(database="postgres", user="postgres", password="postgres", host="localhost", port="5432")
        cur = conn.cursor()
        select_query = "SELECT * FROM {}".format(table_name)
        cur.execute(select_query)
        rows = cur.fetchall()
        
        if len(rows) == 0:
            return True
        else:
            return False
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def init_insert_db_cache():
    conn = None
    try:         
     
        conn = psycopg2.connect(database="postgres", user="postgres", password="postgres", host="localhost", port="5432")
        cur = conn.cursor()

        update_query = "INSERT INTO api_coords_cache (id, value, time_stamp) VALUES (1, %s, %s)"
        
     
        cur.execute(update_query, (pickle.dumps({}),'2022-05-02 14:39:18+00'))  
       
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


'''
Connect to Postgres database
Insert in table "coords_cache" values
'''
def save_db_cache(dictionaries: dict):    

    conn = None
    try:         
     
        conn = psycopg2.connect(database="postgres", user="postgres", password="postgres", host="localhost", port="5432")
        cur = conn.cursor()
        insert_query = "INSERT INTO api_coords_cache (id, value) VALUES (%s, %s)"
        cur.execute(insert_query, (1, pickle.dumps(dictionaries)))   
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
        conn = psycopg2.connect( database="postgres", user="postgres", password="postgres", host="localhost", port="5432")
        cur = conn.cursor()
        select_query = "SELECT * FROM api_coords_cache WHERE id = 1"
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

''' 
Connect to Postgres database
Update table "coords_cache" values
'''
def update_db_cache(dictionaries: dict):
    conn = None
    try:         
     
        conn = psycopg2.connect( database="postgres", user="postgres", password="postgres", host="localhost", port="5432")
        cur = conn.cursor()
        update_query = "UPDATE api_coords_cache SET value = %s WHERE id = %s"
        cur.execute(update_query, (pickle.dumps(dictionaries), 1))   
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
           

if __name__ == '__main__':
    #save_db_cache()
    var = read_db_cache()
    print(type(var))