import pytest
from fastapi.testclient import TestClient
from app import crud

def test_websocket_without_auth(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/1"):
            pass

def test_websocket_with_invalid_token(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/1?token=invalid"):
            pass

def test_websocket_handshake_with_auth(client, db_session):
    user = crud.create_user(db_session, "wsuser", "ws@example.com", "hashedpw")
    
    from app.auth import create_access_token
    token = create_access_token({"sub": "wsuser"})
    
    room = crud.create_chatroom(db_session, "WS Test Room")
    
    with client.websocket_connect(f"/ws/{room.id}?token={token}") as websocket:
        data = websocket.receive_json()
        assert "joined the room" in data["content"]
