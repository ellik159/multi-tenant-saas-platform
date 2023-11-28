from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.session import get_db, set_tenant_context
from src.core.security import get_current_user_token
from src.models.base import Organization
from src.schemas import OrganizationResponse, OrganizationUpdate, MessageResponse

router = APIRouter()


@router.get("/me", response_model=OrganizationResponse)
async def get_current_organization(
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """
    Get current user's organization
    """
    organization_id = current_user.get("organization_id")
    
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return organization


@router.patch("/me", response_model=OrganizationResponse)
async def update_current_organization(
    update_data: OrganizationUpdate,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """
    Update current organization (admin only)
    """
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update organization settings"
        )
    
    organization_id = current_user.get("organization_id")
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Update fields
    if update_data.name is not None:
        organization.name = update_data.name
    
    db.commit()
    db.refresh(organization)
    
    return organization
