import pytest

def test_student_registration(client):
    reg_data = {
        "email": "new.student@apex.edu.lk",
        "password": "securepassword123",
        "full_name": "Nimal Perera",
        "student_index": "2026/SE/999",
        "faculty": "Faculty of Computing"
    }
    response = client.post("/api/auth/register", json=reg_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new.student@apex.edu.lk"
    assert data["role"] == "STUDENT"  # Public registration strictly creates STUDENT

def test_login_success(client):
    response = client.post("/api/auth/login", json={
        "email": "student@apex.edu.lk",
        "password": "student123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "student@apex.edu.lk"
    assert data["user"]["role"] == "STUDENT"

def test_login_invalid_password(client):
    response = client.post("/api/auth/login", json={
        "email": "student@apex.edu.lk",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_get_current_user_profile(client, student_auth_headers):
    response = client.get("/api/auth/me", headers=student_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "student@apex.edu.lk"
    assert data["role"] == "STUDENT"

def test_unauthenticated_request_rejected(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
