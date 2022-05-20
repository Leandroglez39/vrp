import pandas as pd
import psycopg2
import sqlalchemy as sa

'''
Insert csv into a postgres database
'''
def insert_csv_into_db():
    # Load csv into pandas dataframe
    df = pd.read_csv('datos.csv')

    # Create connection to database
    conn = psycopg2.connect( database="postgres", user="postgres", password="postgres", host="localhost", port="5432")
       

    # Create cursor
    cur = conn.cursor()
    print(df["Código_Postal"])
    # Create table   
    cur.execute("INSERT INTO TABLE {} ({})".format("api_zip_code", df['Código_Postal'].to_sql(name='api_zip_code', con=conn)))

    # Commit changes
    conn.commit()

    # Close connection
    conn.close()


def insert():
    # Load csv into pandas dataframe
    df = pd.read_csv('datos.csv')

    engine = sa.create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
    df["Lugar"].drop_duplicates().to_sql('api_lugar', con = engine, if_exists='replace')



if __name__ == '__main__':
   insert()