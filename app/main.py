from fastapi import FastAPI, WebSocket, Depends, HTTPException, status, Response, Query
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional
import json

from app.database import create_db_and_tables, get_db
from app.auth import (
    get_current_user,
    authenticate_user,
    create_access_token,
    get_password_hash,
    validate_websocket_auth,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app import crud, schemas, models

app = FastAPI()
security = HTTPBearer()

connected_clients = {}

@app.on_event("startup")
async def startup():
    create_db_and_tables()

@app.get("/")
async def home():
    try:
        with open("frontend/templates/index.html") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>Chat Application</h1><p>WebSocket chat is available at /ws/{room_id}</p>")

@app.post("/auth/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user_data.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = crud.get_user_by_email(db, user_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_data.password)
    user = crud.create_user(db, user_data.username, user_data.email, hashed_password)
    return user

@app.post("/auth/login", response_model=schemas.Token)
async def login(response: Response, user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}

@app.get("/auth/me", response_model=schemas.UserResponse)
async def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.post("/rooms", response_model=schemas.ChatroomResponse)
async def create_room(
    room_data: schemas.ChatroomCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    room = crud.create_chatroom(db, room_data.name, room_data.theme)
    return room

@app.get("/rooms/{room_id}/messages", response_model=List[schemas.MessageResponse])
async def get_room_messages(
    room_id: int,
    limit: int = Query(default=50, le=100),
    db: Session = Depends(get_db)
):
    room = crud.get_chatroom(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    messages = crud.get_messages(db, room_id, limit)
    return list(reversed(messages))

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    token: Optional[str] = Query(None)
):
    db = next(get_db())
    
    try:
        user = await validate_websocket_auth(token, db)
        
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        room = crud.get_chatroom(db, room_id)
        if not room:
            room = crud.create_chatroom(db, f"Room {room_id}")
        
        await websocket.accept()
        
        if room_id not in connected_clients:
            connected_clients[room_id] = []
        connected_clients[room_id].append(websocket)
        
        join_message = crud.create_message(
            db, room_id, f"{user.username} joined the room", None, "system"
        )
        
        for client in connected_clients[room_id]:
            try:
                await client.send_json({
                    "id": join_message.id,
                    "user": None,
                    "username": "System",
                    "content": join_message.content,
                    "role": join_message.role,
                    "created_at": str(join_message.created_at)
                })
            except:
                pass
        
        try:
            while True:
                data = await websocket.receive_text()
                
                message_data = json.loads(data)
                content = message_data.get("content", data)
                
                db_message = crud.create_message(
                    db, room_id, content, user.id, "user"
                )
                
                message_payload = {
                    "id": db_message.id,
                    "user_id": user.id,
                    "username": user.username,
                    "content": db_message.content,
                    "role": db_message.role,
                    "created_at": str(db_message.created_at)
                }
                
                for client in connected_clients[room_id]:
                    try:
                        await client.send_json(message_payload)
                    except:
                        connected_clients[room_id].remove(client)
        
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            if websocket in connected_clients.get(room_id, []):
                connected_clients[room_id].remove(websocket)
            
            leave_message = crud.create_message(
                db, room_id, f"{user.username} left the room", None, "system"
            )
            
            for client in connected_clients.get(room_id, []):
                try:
                    await client.send_json({
                        "id": leave_message.id,
                        "user": None,
                        "username": "System",
                        "content": leave_message.content,
                        "role": leave_message.role,
                        "created_at": str(leave_message.created_at)
                    })
                except:
                    pass
            
            if room_id in connected_clients and not connected_clients[room_id]:
                del connected_clients[room_id]
    
    finally:
        db.close()
