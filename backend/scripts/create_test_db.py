import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn = psycopg2.connect("dbname=postgres user=postgres password=1234 host=localhost port=5432")
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

try:
    cur.execute("CREATE DATABASE transitops_test;")
    print("Created transitops_test database.")
except Exception as e:
    print(f"Error creating database: {e}")

cur.close()
conn.close()
