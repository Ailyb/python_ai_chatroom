from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Chatroom(Base):
    __tablename__ = "chatrooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    theme = Column(String)
