import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from app.core.database import Base
import app.models  # Ensure all models are imported

engine = create_engine("postgresql+psycopg2://postgres:1234@localhost:5432/transitops")

print("Creating all tables in PostgreSQL...")
Base.metadata.create_all(bind=engine)
print("Done!")
