import pytest
from fastapi.testclient import TestClient

def test_signup(client):
    response = client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_signup_duplicate_username(client):
    client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "test1@example.com",
            "password": "testpassword123"
        }
    )
    response = client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()

def test_login(client):
    client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

def test_get_me(client):
    client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    login_response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    
    response = client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

def test_get_me_unauthorized(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
