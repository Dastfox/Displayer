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

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)