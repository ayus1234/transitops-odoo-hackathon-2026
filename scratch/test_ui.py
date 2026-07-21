import os
import sys
import requests
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
os.environ["DATABASE_URL"] = "postgresql+psycopg2://postgres:1234@localhost:5432/transitops"
os.environ["SECRET_KEY"] = "thisisasecretkeyforlocaldevelopmentonly123"

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import create_access_token
from datetime import timedelta

def test():
    db = SessionLocal()
    user = db.query(User).filter(User.email.ilike('%admin%')).first()
    if not user:
        return
        
    token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(minutes=60))
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Testing /api/v1/reports/trips?export_format=json")
    res2 = requests.get("http://localhost:8000/api/v1/reports/trips?export_format=json", headers=headers)
    print("Response for trips:", res2.text[:500])
    
if __name__ == "__main__":
    test()

