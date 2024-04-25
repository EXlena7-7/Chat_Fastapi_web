from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from dataclasses import dataclass
from typing import Dict
import uuid
import json
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

@dataclass
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connection: dict = {} # Corregido aquí

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        id = str(uuid.uuid4())

        self.active_connection[id] = websocket # Ahora coincide con el nombre correcto
        data = json.dumps({"isMe": True, "data":"Bienvenido!!", "username":"Tú"})
        await self.send_message(websocket, data)
    
    async def send_message(self, ws:WebSocket, message: str):
        await ws.send_text(message)

    async def broadcast(self, websocket: WebSocket, data: str):
        decoded_data = json.loads(data)    
        for connection in self.active_connection.values(): # Ahora coincide con el nombre correcto
            is_me = False
            if connection == websocket:
                is_me = True
            await connection.send_text(json.dumps({"isMe": is_me, "data": decoded_data['message'], "username": decoded_data['username']}))  

    async def disconnect(self, websocket: WebSocket):
        id = self.find_id(WebSocket) 
        del self.active_connection[id] 
        
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
template = Jinja2Templates(directory="templates")

@app.get("/")
async def get_app(request: Request):
    # Utiliza el objeto template para renderizar la plantilla 'index.html'
    return template.TemplateResponse("index.html", {"request": request, "title": "Chat app 2"})

connection_manager = ConnectionManager()

@app.websocket("/message")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            await connection_manager.broadcast(websocket, data)
    except WebSocketDisconnect:
        return RedirectResponse("/")


        
        
