# app/models/websocket.py
import logging

from fastapi import WebSocket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSocketManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not WebSocketManager._initialized:
            self.clients = []
            self.current_file = None
            self.current_file_url = None
            WebSocketManager._initialized = True
            logger.info("WebSocket Manager initialized")

    async def connect(self, websocket: WebSocket):
        print(self.current_file)
        await websocket.accept()
        self.clients.append(websocket)
        logger.info(f"New client connected. Total clients: {len(self.clients)}")
        logger.info(f"Client list: {self.clients}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.clients:
            self.clients.remove(websocket)
            logger.info(f"Client disconnected. Remaining clients: {len(self.clients)}")
            logger.info(f"Client list: {self.clients}")

    async def broadcast(self, message: str):
        logger.info(f"Broadcasting message: {message}")
        logger.info(f"Total clients before broadcast: {len(self.clients)}")
        logger.info(f"Client list before broadcast: {self.clients}")

        disconnected_clients = []
        for client in self.clients:
            try:
                await client.send_text(message)
                logger.info(f"Successfully sent message to client")
            except Exception as e:
                logger.error(f"Error sending message to client: {str(e)}")
                disconnected_clients.append(client)

        for client in disconnected_clients:
            self.disconnect(client)

    def set_current_file(self, file: str | None, url: str):
        self.current_file = file
        self.current_file_url = url
        logger.info(f"Current file set to: {file} with URL: {url}")


# Create a singleton instance
ws_manager = WebSocketManager()