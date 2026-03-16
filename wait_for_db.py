import psycopg2
import time
import os

while True:
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        conn.close()
        break
    except psycopg2.OperationalError:
        print("Waiting for PostgreSQL...")
        time.sleep(1)