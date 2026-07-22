import os
import sys
import random
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.vehicle import Vehicle
from app.models.trip import Trip

def fix_cities_and_vehicles():
    manufacturers = [
        ("Tata Motors", ["Signa", "Prima", "Ultra", "LPT"]),
        ("Ashok Leyland", ["Dost", "Partner", "Boss", "Ecomet", "Captain"]),
        ("Mahindra", ["Blazo", "Furio", "Bolero Pik-Up", "Supro"]),
        ("Eicher", ["Pro 2049", "Pro 3015", "Pro 6028", "Pro 8031"]),
        ("BharatBenz", ["1015R", "1923C", "2823R", "3528C"]),
        ("Force Motors", ["Traveller", "Trump", "Shaktiman", "Urbania"])
    ]
    
    cities = [
        "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Ahmedabad", "Chennai", 
        "Kolkata", "Surat", "Pune", "Jaipur", "Lucknow", "Kanpur", "Nagpur", 
        "Indore", "Thane", "Bhopal", "Visakhapatnam", "Patna", "Vadodara", 
        "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad", "Rajkot"
    ]
    
    state_codes = ["MH", "DL", "KA", "TS", "GJ", "TN", "WB", "UP", "MP", "AP", "BR", "PB", "RJ", "HR", "CG"]
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def gen_reg_number():
        state = random.choice(state_codes)
        rto = f"{random.randint(1, 99):02d}"
        chars = f"{random.choice(letters)}{random.choice(letters)}"
        num = f"{random.randint(1000, 9999)}"
        return f"{state} {rto} {chars} {num}"

    db = SessionLocal()
    try:
        # Update vehicles
        vehicles = db.query(Vehicle).all()
        v_count = 0
        for v in vehicles:
            make_info = random.choice(manufacturers)
            v.manufacturer = make_info[0]
            v.model = random.choice(make_info[1])
            v.vehicle_name = f"{v.manufacturer} {v.model}"
            v.registration_number = gen_reg_number()
            v_count += 1
            
        # Update trips
        trips = db.query(Trip).all()
        t_count = 0
        for t in trips:
            c1, c2 = random.sample(cities, 2)
            t.source = c1
            t.destination = c2
            t_count += 1

        db.commit()
        print(f"Fixed {v_count} vehicles and {t_count} trips with Indian names.")
    finally:
        db.close()

if __name__ == "__main__":
    fix_cities_and_vehicles()
