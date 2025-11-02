import pytest
from app import crud, models

def test_create_message(db_session):
    user = crud.create_user(db_session, "testuser", "test@example.com", "hashedpw")
    room = crud.create_chatroom(db_session, "Test Room")
    
    message = crud.create_message(db_session, room.id, "Hello, world!", user.id, "user")
    
    assert message.id is not None
    assert message.content == "Hello, world!"
    assert message.user_id == user.id
    assert message.room_id == room.id
    assert message.role == "user"

def test_get_messages(db_session):
    user = crud.create_user(db_session, "testuser", "test@example.com", "hashedpw")
    room = crud.create_chatroom(db_session, "Test Room")
    
    msg1 = crud.create_message(db_session, room.id, "Message 1", user.id, "user")
    msg2 = crud.create_message(db_session, room.id, "Message 2", user.id, "user")
    msg3 = crud.create_message(db_session, room.id, "Message 3", user.id, "user")
    
    messages = crud.get_messages(db_session, room.id, limit=10)
    
    assert len(messages) == 3

def test_get_room_messages_api(client):
    signup_response = client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    
    room_response = client.post(
        "/rooms",
        json={"name": "Test Room"}
    )
    room_id = room_response.json()["id"]
    
    response = client.get(f"/rooms/{room_id}/messages")
    assert response.status_code == 200
    messages = response.json()
    assert isinstance(messages, list)
