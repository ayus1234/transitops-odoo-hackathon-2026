import os
import sys
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

def debug_call():
    client = TestClient(app)
    
    # Login as admin to get token
    response = client.post("/api/v1/auth/login", json={"email": "admin@transitops.com", "password": "testpass123"})
    if response.status_code != 200:
        print("Login failed:", response.json())
        return
        
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Call scheduler
    res = client.get("/api/v1/maintenance/scheduler", headers=headers)
    print("STATUS:", res.status_code)
    print("BODY:", res.json())

if __name__ == '__main__':
    debug_call()
