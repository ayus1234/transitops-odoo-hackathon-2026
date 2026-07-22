import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.database import engine, Base
import app.models

print('Creating tables...')
Base.metadata.create_all(bind=engine)
print('Tables created!')
