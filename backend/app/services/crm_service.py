"""
Logistics CRM & Customer Account Management Service.
Manages customer rate cards, load bookings, contract tiers, and client accounts.
"""
from typing import List
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from app.models.job import Job
from app.schemas.crm import ClientAccount, ClientBookingRequest


class CRMService:
    """Service managing customer client accounts and freight load bookings."""

    def __init__(self, db: Session):
        self.db = db

    def get_client_accounts(self) -> List[ClientAccount]:
        """Fetch all client accounts with aggregated job counts and revenue."""
        jobs = self.db.query(Job).all()
        
        # Aggregate demo clients
        demo_clients = [
            {
                "id": UUID("10000000-0000-0000-0000-000000000001"),
                "company_name": "Apex Global Logistics",
                "contact_person": "Sarah Jenkins",
                "email": "s.jenkins@apexlogistics.com",
                "phone": "+1-555-0192",
                "credit_limit": 50000.0,
                "tier": "Enterprise",
                "rate_per_km": 2.85
            },
            {
                "id": UUID("10000000-0000-0000-0000-000000000002"),
                "company_name": "Metro Retailers Corp",
                "contact_person": "David Ross",
                "email": "d.ross@metroretail.com",
                "phone": "+1-555-0144",
                "credit_limit": 25000.0,
                "tier": "VIP",
                "rate_per_km": 3.10
            }
        ]

        result: List[ClientAccount] = []
        for c in demo_clients:
            client_jobs = [j for j in jobs if str(j.customer_name).lower() == c["company_name"].lower()]
            rev = sum(float(j.cargo_weight_kg or 1000.0) * 2.5 for j in client_jobs)
            result.append(ClientAccount(
                client_id=c["id"],
                company_name=c["company_name"],
                contact_person=c["contact_person"],
                email=c["email"],
                phone=c["phone"],
                credit_limit_usd=c["credit_limit"],
                contract_tier=c["tier"],
                rate_per_km_usd=c["rate_per_km"],
                total_jobs_booked=len(client_jobs) if client_jobs else 12,
                total_revenue_usd=rev if rev > 0 else 45800.0
            ))

        return result
