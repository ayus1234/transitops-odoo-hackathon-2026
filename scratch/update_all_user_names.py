import sys
import os
import random
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
os.environ["DATABASE_URL"] = "postgresql+psycopg2://postgres:1234@localhost:5432/transitops"
os.environ["SECRET_KEY"] = "thisisasecretkeyforlocaldevelopmentonly123"

from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()

# Only Indian MEN names
first_names = [
    "Rahul", "Amit", "Vikram", "Suresh", "Ramesh", "Rajesh", "Deepak", "Sunil", "Anil", "Sanjay", 
    "Manoj", "Ashok", "Vijay", "Raju", "Prakash", "Ganesh", "Santosh", "Pramod", "Kishore", "Dinesh",
    "Arjun", "Aditya", "Ravi", "Harish", "Navin", "Nitin", "Praveen", "Sachin", "Vishal", "Yash",
    "Prashant", "Mukesh", "Suraj", "Nikhil", "Tarun", "Gaurav", "Rohit", "Mohit", "Aman", "Abhishek"
]

last_names = [
    "Kumar", "Sharma", "Singh", "Patel", "Gupta", "Yadav", "Verma", "Das", "Mishra", "Pandey", 
    "Reddy", "Rao", "Chauhan", "Choudhary", "Jadhav", "Deshmukh", "Pawar", "Bhatt", "Joshi", "Nair",
    "Iyer", "Menon", "Pillai", "Chakraborty", "Banerjee", "Chatterjee", "Sen", "Bose", "Ghosh", "Datta"
]

users = db.query(User).all()
updated_count = 0

for user in users:
    if user.email == "admin@transitops.com":
        user.first_name = "Arjun"
        user.last_name = "Kapoor"
    else:
        user.first_name = random.choice(first_names)
        user.last_name = random.choice(last_names)
    updated_count += 1

db.commit()
print(f"Successfully updated {updated_count} user names to authentic Indian men names!")
db.close()
