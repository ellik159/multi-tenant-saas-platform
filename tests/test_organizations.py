import pytest
from fastapi import status


def test_get_current_organization(client, get_auth_headers, test_user_credentials):
    """Test getting current organization"""
    headers = get_auth_headers()
    
    response = client.get("/api/v1/organizations/me", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == test_user_credentials["organization_name"]
    assert data["slug"] == test_user_credentials["organization_slug"]
    assert data["subscription_tier"] == "free"


def test_update_organization_as_admin(client, get_auth_headers):
    """Test updating organization as admin"""
    headers = get_auth_headers()
    
    update_data = {"name": "Updated Org Name"}
    response = client.patch("/api/v1/organizations/me", json=update_data, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Org Name"
