import psycopg2
try:
    conn = psycopg2.connect("dbname=transitops user=postgres password=1234 host=localhost port=5432")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    print("Schema dropped and recreated successfully.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Failed: {e}")
