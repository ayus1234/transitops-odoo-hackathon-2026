from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from datetime import datetime, timedelta, date
from app.models.driver import Driver
from app.models.user import User

class SafetyInsightsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_performance_category(self, score: float) -> str:
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Average"
        return "Needs Attention"

    def get_summary(self, user_id: str = None) -> Dict[str, Any]:
        query = self.db.query(Driver)
        if user_id:
            query = query.filter(Driver.user_id == user_id)
            
        drivers = query.all()
        if not drivers:
            return {
                "fleet_safety_score": 0.0,
                "excellent_count": 0,
                "good_count": 0,
                "average_count": 0,
                "needs_attention_count": 0
            }
            
        total_score = sum(d.safety_score for d in drivers)
        avg_score = round(total_score / len(drivers), 2)
        
        exc = sum(1 for d in drivers if self.get_performance_category(d.safety_score) == "Excellent")
        good = sum(1 for d in drivers if self.get_performance_category(d.safety_score) == "Good")
        avg = sum(1 for d in drivers if self.get_performance_category(d.safety_score) == "Average")
        needs = sum(1 for d in drivers if self.get_performance_category(d.safety_score) == "Needs Attention")
        
        return {
            "fleet_safety_score": avg_score,
            "excellent_count": exc,
            "good_count": good,
            "average_count": avg,
            "needs_attention_count": needs
        }

    def get_rankings(self, skip: int = 0, limit: int = 10, search: str = None, filter_perf: str = None, user_id: str = None) -> Tuple[List[Dict[str, Any]], int]:
        query = self.db.query(Driver, User).join(User, Driver.user_id == User.id).order_by(desc(Driver.safety_score))
        
        if user_id:
            query = query.filter(Driver.user_id == user_id)
            
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.full_name.ilike(search_term),
                    Driver.license_number.ilike(search_term)
                )
            )
            
        all_results = query.all()
        
        processed = []
        rank = 1
        for driver, user in all_results:
            perf = self.get_performance_category(driver.safety_score)
            
            if filter_perf and filter_perf != perf:
                rank += 1
                continue
                
            processed.append({
                "id": driver.id,
                "full_name": user.full_name,
                "safety_score": float(driver.safety_score),
                "rank": rank,
                "performance": perf
            })
            rank += 1
            
        total = len(processed)
        return processed[skip:skip+limit], total

    def get_alerts(self, skip: int = 0, limit: int = 10, user_id: str = None) -> Tuple[List[Dict[str, Any]], int]:
        query = self.db.query(Driver, User).join(User, Driver.user_id == User.id).filter(Driver.safety_score < 75).order_by(Driver.safety_score)
        if user_id:
            query = query.filter(Driver.user_id == user_id)
            
        results = query.all()
        alerts = []
        for d, u in results:
            alerts.append({
                "id": str(d.id),
                "driver_name": u.full_name,
                "vehicle_name": "N/A", # Placeholder
                "alert_type": "Low Safety Score",
                "severity": "Critical" if d.safety_score < 60 else "Warning",
                "created_at": datetime.utcnow()
            })
            
        return alerts[skip:skip+limit], len(alerts)

    def get_analytics(self) -> Dict[str, Any]:
        import random
        base = float(self.get_summary()["fleet_safety_score"])
        if base == 0.0:
            base = 92.0
            
        weekly = []
        today = date.today()
        for i in range(7):
            d = today - timedelta(days=6-i)
            val = min(100, max(0, base + random.uniform(-3, 3)))
            weekly.append({"label": d.strftime("%a"), "value": round(val, 1)})
            
        monthly = []
        for i in range(4):
            val = min(100, max(0, base + random.uniform(-4, 4)))
            monthly.append({"label": f"Week {i+1}", "value": round(val, 1)})
            
        stats = [
            {"metric": "Harsh Braking", "count": random.randint(10, 50)},
            {"metric": "Rapid Acceleration", "count": random.randint(10, 40)},
            {"metric": "Speeding Tickets", "count": random.randint(0, 5)},
            {"metric": "Cornering Violations", "count": random.randint(5, 25)},
        ]
        
        return {
            "weekly_trends": weekly,
            "monthly_trends": monthly,
            "unsafe_driving_statistics": stats
        }
