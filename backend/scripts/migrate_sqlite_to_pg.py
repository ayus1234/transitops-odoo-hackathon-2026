import os
import sys
import uuid
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, MetaData, select, text
from sqlalchemy.orm import sessionmaker

sqlite_url = "sqlite:///./transitops.db"
pg_url = "postgresql+psycopg2://postgres:1234@localhost:5432/transitops"

print(f"Connecting to SQLite: {sqlite_url}")
sqlite_engine = create_engine(sqlite_url)
sqlite_meta = MetaData()
sqlite_meta.reflect(bind=sqlite_engine)

print(f"Connecting to PostgreSQL: {pg_url}")
pg_engine = create_engine(pg_url)
pg_meta = MetaData()
pg_meta.reflect(bind=pg_engine)

pg_session = sessionmaker(bind=pg_engine)()

def process_row(table, row_proxy):
    row = dict(row_proxy._mapping)
    
    # Process types
    for col in table.columns:
        val = row.get(col.name)
        if val is None:
            continue
            
        # Handle SQLite JSON strings (they need to be parsed to dict/list for pg JSONB)
        if str(col.type).startswith("JSON") and isinstance(val, str):
            try:
                row[col.name] = json.loads(val)
            except:
                pass
                
        # Handle UUIDs
        if str(col.type) == 'UUID' and isinstance(val, str):
            try:
                row[col.name] = uuid.UUID(val)
            except:
                pass
                
        # Handle Float/Numeric if they come out as strings
        if 'NUMERIC' in str(col.type).upper() or 'FLOAT' in str(col.type).upper():
            if isinstance(val, str) and val.strip() != "":
                try:
                    row[col.name] = float(val)
                except:
                    pass
        
        # Handle booleans (SQLite stores as 0/1)
        if str(col.type) == 'BOOLEAN':
            row[col.name] = bool(val)
            
    return row

print("Disabling foreign key checks in PostgreSQL for import...")
pg_session.execute(text("SET session_replication_role = replica;"))
pg_session.commit()

for table_name in sqlite_meta.tables:
    if table_name == 'alembic_version':
        continue
        
    sqlite_table = sqlite_meta.tables[table_name]
    pg_table = pg_meta.tables.get(table_name)
    
    if pg_table is None:
        print(f"Skipping table {table_name}: Not found in PostgreSQL")
        continue
        
    print(f"Migrating table {table_name}...")
    
    # Read from SQLite using raw SQL to avoid type processor crashes
    with sqlite_engine.connect() as sqlite_conn:
        result = sqlite_conn.execute(text(f"SELECT * FROM {table_name}"))
        rows_to_insert = [process_row(pg_table, row) for row in result]
        
    if rows_to_insert:
        # Delete existing just in case (though it should be empty)
        with pg_engine.begin() as pg_conn:
            pg_conn.execute(pg_table.delete())
            # Insert
            pg_conn.execute(pg_table.insert(), rows_to_insert)
        
    print(f"  -> Migrated {len(rows_to_insert)} rows")

print("Re-enabling foreign key checks in PostgreSQL...")
pg_session.execute(text("SET session_replication_role = DEFAULT;"))
pg_session.commit()
pg_session.close()

print("Migration completed successfully!")
