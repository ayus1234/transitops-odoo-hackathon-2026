import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn = psycopg2.connect("dbname=postgres user=postgres password=1234 host=localhost port=5432")
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

try:
    # Force disconnect other clients
    cur.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'transitops' AND pid <> pg_backend_pid();")
    cur.execute("DROP DATABASE IF EXISTS transitops;")
    print("Dropped transitops database.")
except Exception as e:
    print(f"Error dropping database: {e}")

cur.execute("CREATE DATABASE transitops;")
print("Created transitops database.")

cur.close()
conn.close()
