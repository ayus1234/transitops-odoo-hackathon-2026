import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    conn = psycopg2.connect("dbname=postgres user=postgres password=1234 host=localhost port=5432")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("CREATE DATABASE transitops;")
    print("Database transitops created successfully.")
    cur.execute("CREATE DATABASE transitops_test;")
    print("Database transitops_test created successfully.")
    cur.close()
    conn.close()
except psycopg2.errors.DuplicateDatabase:
    print("Database already exists.")
except Exception as e:
    print(f"Failed to create databases: {e}")
