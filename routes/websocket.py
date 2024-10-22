from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from models.websocket import ws_manager  # Import the singleton instance
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/{client_type}")
async def websocket_endpoint(websocket: WebSocket, client_type: str):
    await ws_manager.connect(websocket)

    try:
        if ws_manager.current_file_url:
            logger.info(f"Sending current file URL to new client: {ws_manager.current_file_url}")
            await websocket.send_text(ws_manager.current_file_url)

        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message from client: {data}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {client_type}")
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}")
        ws_manager.disconnect(websocket)