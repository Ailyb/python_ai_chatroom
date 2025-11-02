from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app import models

def create_user(db: Session, username: str, email: str, hashed_password: str) -> models.User:
    db_user = models.User(username=username, email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_chatroom(db: Session, name: str, theme: str = None) -> models.Chatroom:
    db_chatroom = models.Chatroom(name=name, theme=theme)
    db.add(db_chatroom)
    db.commit()
    db.refresh(db_chatroom)
    return db_chatroom

def get_chatroom(db: Session, room_id: int) -> Optional[models.Chatroom]:
    return db.query(models.Chatroom).filter(models.Chatroom.id == room_id).first()

def create_message(db: Session, room_id: int, content: str, user_id: Optional[int] = None, role: str = "user") -> models.Message:
    db_message = models.Message(
        room_id=room_id,
        user_id=user_id,
        content=content,
        role=role
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages(db: Session, room_id: int, limit: int = 50) -> List[models.Message]:
    return db.query(models.Message).filter(
        models.Message.room_id == room_id
    ).order_by(models.Message.created_at.desc()).limit(limit).all()

def create_session(db: Session, user_id: int, expires_at: datetime) -> models.Session:
    db_session = models.Session(user_id=user_id, expires_at=expires_at)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def delete_session(db: Session, session_id: int) -> None:
    db_session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if db_session:
        db.delete(db_session)
        db.commit()
