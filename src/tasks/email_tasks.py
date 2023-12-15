from src.tasks.celery_app import celery_app


@celery_app.task(name="src.tasks.email_tasks.send_welcome_email")
def send_welcome_email(user_email: str, organization_name: str):
    """
    Send welcome email to new user
    TODO: implement actual email sending
    """
    print(f"Sending welcome email to {user_email} for org {organization_name}")
    # In production, use an email service like SendGrid, SES, etc.
    return {"status": "sent", "email": user_email}


@celery_app.task(name="src.tasks.email_tasks.send_subscription_confirmation")
def send_subscription_confirmation(user_email: str, tier: str):
    """
    Send subscription confirmation email
    """
    print(f"Sending subscription confirmation to {user_email} for tier {tier}")
    return {"status": "sent", "email": user_email}


@celery_app.task(name="src.tasks.email_tasks.send_invoice")
def send_invoice(user_email: str, invoice_url: str):
    """
    Send invoice email
    """
    print(f"Sending invoice to {user_email}: {invoice_url}")
    return {"status": "sent", "email": user_email}
