import pytest
from fastapi import status


def test_get_current_user(client, get_auth_headers):
    """Test getting current user profile"""
    headers = get_auth_headers()
    
    response = client.get("/api/v1/users/me", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "email" in data
    assert data["role"] == "admin"  # First user is admin


def test_list_users_as_admin(client, get_auth_headers):
    """Test listing users as admin"""
    headers = get_auth_headers()
    
    response = client.get("/api/v1/users/", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # At least the registered user


def test_create_user_as_admin(client, get_auth_headers):
    """Test creating a user as admin"""
    headers = get_auth_headers()
    
    new_user = {
        "email": "newuser@example.com",
        "password": "newpassword123",
        "full_name": "New User",
        "role": "member"
    }
    
    response = client.post("/api/v1/users/", json=new_user, headers=headers)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == new_user["email"]
    assert data["role"] == "member"


def test_unauthorized_access(client):
    """Test accessing protected endpoint without auth"""
    response = client.get("/api/v1/users/me")
    
    # Should fail without auth header
    assert response.status_code in [401, 403]
