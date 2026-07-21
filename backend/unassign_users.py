import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User

def main():
    db = SessionLocal()
    try:
        # Get the last 3 users who are currently drivers
        users = db.query(User).filter(User.email.like("driver.%")).limit(3).all()

        for user in users:
            user.role_id = None
            user.additional_roles = []
            
        db.commit()
        print(f"Successfully unassigned roles for {len(users)} users.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
