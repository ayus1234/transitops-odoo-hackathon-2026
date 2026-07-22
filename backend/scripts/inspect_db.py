import psycopg2
from pprint import pprint

conn = psycopg2.connect("dbname=transitops user=postgres password=1234 host=localhost port=5432")
cur = conn.cursor()

cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
""")
tables = cur.fetchall()
print("Tables in public schema:")
pprint(tables)

cur.close()
conn.close()
