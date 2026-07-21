import sys
import os
import random
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
os.environ["DATABASE_URL"] = "postgresql+psycopg2://postgres:1234@localhost:5432/transitops"
os.environ["SECRET_KEY"] = "thisisasecretkeyforlocaldevelopmentonly123"

from app.core.database import SessionLocal
from app.models.driver import Driver
from app.models.user import User

db = SessionLocal()

first_names = [
    "Rahul", "Amit", "Vikram", "Suresh", "Ramesh", "Rajesh", "Deepak", "Sunil", "Anil", "Sanjay", 
    "Manoj", "Ashok", "Vijay", "Raju", "Prakash", "Ganesh", "Santosh", "Pramod", "Kishore", "Dinesh"
]

last_names = [
    "Kumar", "Sharma", "Singh", "Patel", "Gupta", "Yadav", "Verma", "Das", "Mishra", "Pandey", 
    "Reddy", "Rao", "Chauhan", "Choudhary", "Jadhav", "Deshmukh", "Pawar", "Bhatt", "Joshi", "Nair"
]

drivers = db.query(Driver).all()
updated_count = 0

for driver in drivers:
    user = db.query(User).filter(User.id == driver.user_id).first()
    if user:
        user.first_name = random.choice(first_names)
        user.last_name = random.choice(last_names)
        updated_count += 1

db.commit()
print(f"Successfully updated {updated_count} driver names to authentic Indian names!")
db.close()
