# python_ai_chatroom

A chatroom web application built with FastAPI and WebSockets. Users can join chatrooms and exchange real-time messages. The backend uses FastAPI, SQLAlchemy, and PostgreSQL. The frontend is a simple HTML/JS interface.

## Features

- Real-time chat using WebSockets
- User and chatroom models (SQLAlchemy)
- PostgreSQL database integration
- Simple HTML/JS frontend

## Requirements

- Python 3.10+
- PostgreSQL
- Install dependencies:
  ```bash
  pip install fastapi uvicorn sqlalchemy psycopg2
  ```

## Setup

1. Configure the database
Edit database.py and set your PostgreSQL credentials in DATABASE_URL.

2. Initialize the database
The tables will be created automatically on app startup.

3. Run the FastAPI server
From the project root, run: uvicorn app.main:app --reload or, if using app.py: python app.py

4. Open the chatroom
Visit http://localhost:8000 in your browser (which is likely http://127.0.0.1:8000/ if running locally in windows vs code IDE).


## Project Structure

app/ main.py # FastAPI app and WebSocket endpoint database.py # SQLAlchemy setup models.py # Database models frontend/ templates/ index.html # Main chatroom frontend assets/ index.html # (Optional) Alternative frontend

## Notes

- The default frontend is at frontend/templates/index.html.
- WebSocket endpoint: /ws/{chatroom_id}