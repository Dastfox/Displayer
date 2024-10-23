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
            self.current_background = None  # Add background tracking
            self.show_journal_button = False
            WebSocketManager._initialized = True
            logger.info("WebSocket Manager initialized")

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.clients.append(websocket)
        # Send current state to new client
        if self.current_background:
            await websocket.send_json({"type": "background", "path": self.current_background})
        logger.info(f"New client connected. Total clients: {len(self.clients)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.clients:
            self.clients.remove(websocket)
            logger.info(f"Client disconnected. Remaining clients: {len(self.clients)}")

    async def broadcast(self, message: str | dict):
        logger.info(f"Broadcasting message: {message}")
        disconnected_clients = []

        for client in self.clients:
            try:
                if isinstance(message, dict):
                    await client.send_json(message)
                else:
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

    def set_background(self, background_path: str | None):
        self.current_background = background_path
        logger.info(f"Current background set to: {background_path}")

    async def broadcast_background(self, background_path: str):
        """Broadcast the current background to all clients"""
        message = {
            "type": "background",
            "path": background_path
        }
        await self.broadcast(message)

    async def broadcast_journal_state(self):
        """Broadcast the current journal button state to all clients"""
        message = {
            "type": "journal_state",
            "show_journal_button": self.show_journal_button
        }
        await self.broadcast(message)


# Create a singleton instance
ws_manager = WebSocketManager()