"""Integration tests for authentication endpoints."""

import pytest


@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["is_active"] is True
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    await client.post(
        "/auth/register",
        json={
            "email": "dup@example.com",
            "username": "user1",
            "password": "password123",
        },
    )
    response = await client.post(
        "/auth/register",
        json={
            "email": "dup@example.com",
            "username": "user2",
            "password": "password456",
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "mypassword",
        },
    )
    response = await client.post(
        "/auth/login",
        json={"username": "loginuser", "password": "mypassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(client):
    await client.post(
        "/auth/register",
        json={
            "email": "wrong@example.com",
            "username": "wronguser",
            "password": "correctpassword",
        },
    )
    response = await client.post(
        "/auth/login",
        json={"username": "wronguser", "password": "wrongpassword"},
    )
    assert response.status_code == 401
