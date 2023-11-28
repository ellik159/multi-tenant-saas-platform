from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
import stripe

from src.database.session import get_db
from src.core.security import get_current_user_token
from src.core.config import settings
from src.models.base import Organization, SubscriptionTier
from src.schemas import (
    SubscriptionResponse, CreateCheckoutSessionRequest,
    CreateCheckoutSessionResponse, MessageResponse
)

router = APIRouter()

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """
    Get current organization's subscription details
    """
    organization_id = current_user.get("organization_id")
    
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return SubscriptionResponse(
        tier=organization.subscription_tier,
        status=organization.subscription_status,
        stripe_customer_id=organization.stripe_customer_id,
        stripe_subscription_id=organization.stripe_subscription_id
    )


@router.post("/create-checkout", response_model=CreateCheckoutSessionResponse)
async def create_checkout_session(
    request: CreateCheckoutSessionRequest,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """
    Create Stripe checkout session for subscription upgrade
    """
    if not settings.ENABLE_STRIPE_BILLING:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing is currently disabled"
        )
    
    organization_id = current_user.get("organization_id")
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Map tier to Stripe price ID (these would be real Stripe price IDs in production)
    price_mapping = {
        SubscriptionTier.PRO: "price_pro_monthly",  # Replace with actual price ID
        SubscriptionTier.ENTERPRISE: "price_enterprise_monthly"
    }
    
    if request.tier not in price_mapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscription tier"
        )
    
    try:
        # Create or get Stripe customer
        if not organization.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.get("email"),
                metadata={
                    "organization_id": str(organization_id),
                    "organization_name": organization.name
                }
            )
            organization.stripe_customer_id = customer.id
            db.commit()
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=organization.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": price_mapping[request.tier],
                "quantity": 1
            }],
            mode="subscription",
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={
                "organization_id": str(organization_id),
                "tier": request.tier.value
            }
        )
        
        return CreateCheckoutSessionResponse(
            checkout_url=checkout_session.url,
            session_id=checkout_session.id
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )


@router.post("/webhook", response_model=MessageResponse)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events
    """
    if not settings.ENABLE_STRIPE_BILLING:
        return MessageResponse(message="Billing disabled")
    
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle different event types
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        organization_id = session["metadata"]["organization_id"]
        tier = session["metadata"]["tier"]
        
        # Update organization subscription
        organization = db.query(Organization).filter(Organization.id == organization_id).first()
        if organization:
            organization.subscription_tier = SubscriptionTier(tier)
            organization.subscription_status = "active"
            organization.stripe_subscription_id = session.get("subscription")
            db.commit()
    
    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        # Handle subscription updates
        pass
    
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        # Handle subscription cancellation
        # Find org by stripe_subscription_id and downgrade to free
        organization = db.query(Organization).filter(
            Organization.stripe_subscription_id == subscription["id"]
        ).first()
        
        if organization:
            organization.subscription_tier = SubscriptionTier.FREE
            organization.subscription_status = "canceled"
            db.commit()
    
    return MessageResponse(message="Webhook processed")
