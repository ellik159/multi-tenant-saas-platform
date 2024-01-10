#!/bin/bash

# CLI tool for common tasks
# Usage: python -m src.cli <command>

import sys
import argparse
from sqlalchemy.orm import Session

from src.database.session import SessionLocal
from src.models.base import Organization, User, UserRole
from src.core.security import get_password_hash


def create_superuser(email: str, password: str, org_name: str, org_slug: str):
    """Create a superuser and organization"""
    db = SessionLocal()
    
    try:
        # Check if org exists
        org = db.query(Organization).filter(Organization.slug == org_slug).first()
        
        if not org:
            # Create organization
            org = Organization(
                name=org_name,
                slug=org_slug
            )
            db.add(org)
            db.flush()
            print(f"Created organization: {org_name}")
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"User {email} already exists")
            return
        
        # Create admin user
        user = User(
            organization_id=org.id,
            email=email,
            hashed_password=get_password_hash(password),
            full_name="Admin User",
            role=UserRole.ADMIN
        )
        db.add(user)
        db.commit()
        
        print(f"Created admin user: {email}")
        print(f"Organization: {org_name} ({org_slug})")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="CLI tool for Multi-Tenant SaaS")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create superuser command
    superuser_parser = subparsers.add_parser("create-superuser", help="Create a superuser")
    superuser_parser.add_argument("--email", default="admin@example.com", help="Admin email")
    superuser_parser.add_argument("--password", default="admin123", help="Admin password")
    superuser_parser.add_argument("--org-name", default="Default Org", help="Organization name")
    superuser_parser.add_argument("--org-slug", default="default-org", help="Organization slug")
    
    args = parser.parse_args()
    
    if args.command == "create-superuser":
        create_superuser(args.email, args.password, args.org_name, args.org_slug)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
