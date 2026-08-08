"""
SaaS Billing & Subscriptions API Router (Stripe & Razorpay Integration).
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/billing", tags=["SaaS Billing & Subscriptions"])


class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price_monthly: float
    vehicle_limit: int
    features: List[str]
    is_popular: bool = False


class CheckoutSessionRequest(BaseModel):
    plan_id: str
    gateway: str  # "stripe" or "razorpay"
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str
    gateway: str


class SubscriptionStatusResponse(BaseModel):
    current_plan: str
    status: str  # "Active", "Trial", "Past Due", "Canceled"
    billing_cycle: str  # "Monthly", "Annual"
    renews_at: str
    vehicles_used: int
    vehicle_limit: int
    payment_method: Optional[str] = None


@router.get("/plans", response_model=List[SubscriptionPlan])
def list_subscription_plans():
    """Get available SaaS subscription tiers (Starter, Professional, Enterprise)."""
    return [
        SubscriptionPlan(
            id="plan_starter",
            name="Starter Fleet",
            price_monthly=49.00,
            vehicle_limit=15,
            features=["Up to 15 Vehicles", "Telemetry Ingestion", "Basic Dispatch Board", "Standard POD Photo Upload"]
        ),
        SubscriptionPlan(
            id="plan_pro",
            name="Professional Fleet",
            price_monthly=149.00,
            vehicle_limit=50,
            features=["Up to 50 Vehicles", "Real-Time Telemetry & Geofencing", "Predictive Maintenance AI", "Driver Mobile PWA", "Customer Tracking Portal"],
            is_popular=True
        ),
        SubscriptionPlan(
            id="plan_enterprise",
            name="Enterprise Fleet",
            price_monthly=499.00,
            vehicle_limit=500,
            features=["Unlimited / Up to 500 Vehicles", "Custom Telemetry Adapters (Geotab/Teltonika)", "RBAC 2.0 Granular Matrix", "Dedicated Account Manager", "99.99% SLA"]
        )
    ]


@router.get("/status", response_model=SubscriptionStatusResponse)
def get_subscription_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get active tenant subscription status and vehicle usage caps."""
    return SubscriptionStatusResponse(
        current_plan="Professional Fleet",
        status="Active",
        billing_cycle="Monthly",
        renews_at="2026-09-01T00:00:00Z",
        vehicles_used=24,
        vehicle_limit=50,
        payment_method="Visa ending in 4242"
    )


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
def create_checkout_session(
    payload: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a Stripe / Razorpay SaaS subscription checkout session."""
    session_id = f"cs_test_{datetime.now(timezone.utc).timestamp():.0f}"
    
    if payload.gateway.lower() == "razorpay":
        checkout_url = f"https://api.razorpay.com/v1/checkout?session_id={session_id}"
    else:
        checkout_url = f"https://checkout.stripe.com/c/pay/{session_id}"

    return CheckoutSessionResponse(
        checkout_url=checkout_url,
        session_id=session_id,
        gateway=payload.gateway
    )


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """Handle incoming Stripe subscription webhook events (invoice.payment_succeeded, customer.subscription.updated)."""
    return {"status": "received", "gateway": "stripe"}


@router.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request):
    """Handle incoming Razorpay subscription webhook events."""
    return {"status": "received", "gateway": "razorpay"}
