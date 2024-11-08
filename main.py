import socket

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import pages, websocket
from config import HOST, PORT, STATIC_DIR

app = FastAPI()


# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include routers
app.include_router(pages.router)
app.include_router(websocket.router)


def get_local_ip():
    try:
        # Create a socket to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        _ip = s.getsockname()[0]
        s.close()
        return _ip
    except:
        return "Could not determine IP"

if __name__ == "__main__":
    ip = get_local_ip()
    print(f"\n🌐 Access from your phone using: http://{ip}:{PORT}\n")

    uvicorn.run("main:app", host=HOST, port=PORT, reload=True, ssl_keyfile=None, ssl_certfile=None)
