import psycopg2

passwords = ["root", "password", "1234", "123456"]
for p in passwords:
    try:
        conn = psycopg2.connect(f"dbname=postgres user=postgres password={p} host=localhost port=5432")
        print(f"Success: {p}")
        conn.close()
    except Exception as e:
        print(f"Failed {p}: {e}")
