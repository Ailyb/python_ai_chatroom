from fastapi import FastAPI, WebSocket, Depends
from fastapi.responses import HTMLResponse
from app.database import create_db_and_tables
from app.auth import get_current_user

app = FastAPI()

@app.on_event("startup")
async def startup():
    create_db_and_tables()

@app.get("/")
async def home():
    with open("frontend/templates/index.html") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws/{chatroom_id}")
async def websocket_endpoint(websocket: WebSocket, chatroom_id: str):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # Echo the message back for now
        await websocket.send_text(f"You wrote: {data}")
