import pytest
from fastapi import status


def test_register_success(client, test_user_credentials):
    """Test successful user registration"""
    response = client.post("/api/v1/auth/register", json=test_user_credentials)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client, test_user_credentials):
    """Test registration with duplicate email"""
    # Register first user
    client.post("/api/v1/auth/register", json=test_user_credentials)
    
    # Try to register again with same email
    response = client.post("/api/v1/auth/register", json=test_user_credentials)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"].lower()


def test_register_duplicate_slug(client, test_user_credentials):
    """Test registration with duplicate organization slug"""
    # Register first user
    client.post("/api/v1/auth/register", json=test_user_credentials)
    
    # Try to register with same slug but different email
    credentials = test_user_credentials.copy()
    credentials["email"] = "another@example.com"
    response = client.post("/api/v1/auth/register", json=credentials)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_success(client, test_user_credentials):
    """Test successful login"""
    # Register user first
    client.post("/api/v1/auth/register", json=test_user_credentials)
    
    # Login
    login_data = {
        "email": test_user_credentials["email"],
        "password": test_user_credentials["password"]
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(client, test_user_credentials):
    """Test login with wrong password"""
    # Register user first
    client.post("/api/v1/auth/register", json=test_user_credentials)
    
    # Try login with wrong password
    login_data = {
        "email": test_user_credentials["email"],
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token(client, test_user_credentials):
    """Test token refresh"""
    # Register and get tokens
    register_response = client.post("/api/v1/auth/register", json=test_user_credentials)
    refresh_token = register_response.json()["refresh_token"]
    
    # Refresh token
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
