import os
import sys

# Add the backend directory to Python's path so 'from app...' imports work
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.main import app
