import os
import sys
import random
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.driver import Driver
from app.models.user import User
from app.models.maintenance import Maintenance

def fix_all_names():
    first_names = [
        "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
        "Shaurya", "Atharv", "Rahul", "Rohan", "Vikram", "Sanjay", "Amit", "Raj", "Karan", "Rakesh", 
        "Suresh", "Ramesh", "Deepak", "Manish", "Sunil", "Anil", "Rohit", "Mohit", "Kapil", "Tarun", 
        "Varun", "Abhinav", "Ajay", "Akhil", "Akshay", "Alok", "Amar", "Anand", "Ankur", "Ashish",
        "Chetan", "Chirag", "Darshan", "Dev", "Gaurav", "Gautam", "Harish", "Hemant", "Jatin", "Kunal"
    ]
    
    last_names = [
        "Sharma", "Verma", "Gupta", "Patel", "Singh", "Kumar", "Reddy", "Rao", "Das", "Mukherjee",
        "Iyer", "Nair", "Pillai", "Chauhan", "Rajput", "Desai", "Joshi", "Bhatt", "Kapoor", "Malhotra",
        "Mehra", "Chopra", "Ahluwalia", "Agarwal", "Bansal", "Garg", "Jain", "Shah", "Mehta",
        "Tiwari", "Mishra", "Pandey", "Shukla", "Dubey", "Yadav", "Choudhary", "Thakur", "Gowda", "Shetty"
    ]

    db = SessionLocal()
    try:
        # Update all Driver user names
        drivers = db.query(Driver).all()
        d_count = 0
        for driver in drivers:
            user = db.query(User).filter(User.id == driver.user_id).first()
            if user:
                user.first_name = random.choice(first_names)
                user.last_name = random.choice(last_names)
                d_count += 1
        
        # Technician names
        maintenances = db.query(Maintenance).all()
        m_count = 0
        tech_map = {}
        
        for m in maintenances:
            if m.assigned_technician:
                if m.assigned_technician not in tech_map:
                    tech_map[m.assigned_technician] = f"{random.choice(first_names)} {random.choice(last_names)}"
                m.assigned_technician = tech_map[m.assigned_technician]
                m_count += 1

        db.commit()
        print(f"Fixed {d_count} driver users and {m_count} maintenance technician records to full male Indian names.")
    finally:
        db.close()

if __name__ == "__main__":
    fix_all_names()
