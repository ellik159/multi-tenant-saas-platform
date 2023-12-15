from datetime import datetime, timedelta
from src.tasks.celery_app import celery_app
from src.database.session import SessionLocal
from src.models.base import AuditLog


@celery_app.task(name="src.tasks.cleanup_tasks.cleanup_old_audit_logs")
def cleanup_old_audit_logs(days_to_keep: int = 90):
    """
    Delete audit logs older than specified days
    Runs daily via Celery Beat
    """
    db = SessionLocal()
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        deleted_count = db.query(AuditLog).filter(
            AuditLog.timestamp < cutoff_date
        ).delete()
        
        db.commit()
        
        print(f"Deleted {deleted_count} audit logs older than {days_to_keep} days")
        return {"deleted_count": deleted_count, "cutoff_date": cutoff_date.isoformat()}
        
    except Exception as e:
        db.rollback()
        print(f"Error cleaning up audit logs: {e}")
        raise
    finally:
        db.close()


@celery_app.task(name="src.tasks.cleanup_tasks.cleanup_inactive_organizations")
def cleanup_inactive_organizations(days_inactive: int = 180):
    """
    Mark organizations as inactive if no activity for X days
    TODO: implement this properly
    """
    print(f"Checking for organizations inactive for {days_inactive} days")
    # Implementation would check last_activity timestamp
    return {"status": "checked"}
