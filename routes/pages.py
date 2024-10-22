# app/routes/pages.py
import logging
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from service.file_service import FileService
from models.websocket import WebSocketManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()
ws_manager = WebSocketManager()

# Get the base directory path
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"


def get_template(template_name: str) -> str:
    """Read and return the content of a template file"""
    template_path = TEMPLATE_DIR / template_name
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


@router.get("/", response_class=HTMLResponse)
async def home():
    return get_template('home.html')


@router.get("/manager", response_class=HTMLResponse)
async def manager(request: Request):
    files = FileService.get_all_files()
    template = get_template('manager.html')
    buttons = "".join(
        f'<button class="file-button" data-file="{file}" onclick="selectFile(\'{file}\')">{file}</button>'
        for file in files
    )
    buttons = "".join(
        buttons + f"<button class='file-button' onclick=\"selectFile()\">None</button>"
    )
    return template.replace("{{buttons}}", buttons)


@router.get("/select")
async def select_file(file: str | None):
    logger.info(f"File selection request received: {file, type(file)}")
    is_valid, decoded_file = FileService.verify_file(file)

    if file == 'undefined':
        logger.info("Empty file request - redirecting to home")
        ws_manager.set_current_file(None, "/")
        await ws_manager.broadcast("/")
        return JSONResponse(
            status_code=200,
            content={"message": "Redirecting to home page"}
        )


    elif not is_valid:
        logger.error(f"Invalid file requested: {decoded_file}")
        return JSONResponse(
            status_code=404,
            content={"message": f"File '{decoded_file}' not found"}
        )
    else:
        file_url = FileService.generate_unique_url(decoded_file)
        logger.info(f"Generated unique URL for file: {file_url}")

        ws_manager.set_current_file(decoded_file, file_url)
        await ws_manager.broadcast(file_url)
        logger.info("Broadcast complete")

        return JSONResponse(
            content={"message": f"File '{decoded_file}' selected. All clients updated."}
        )


@router.get("/display/{unique_id}", response_class=HTMLResponse)
async def display(unique_id: str):
    if not (ws_manager.current_file and
            ws_manager.current_file_url and
            ws_manager.current_file_url.endswith(unique_id)):
        return RedirectResponse(url="/")

    template = get_template('display.html')

    extension = ws_manager.current_file.split('.').pop().lower()
    if extension == 'html':
        content = FileService.get_file_content(ws_manager.current_file)
    else:
        content = f'<img src="/static/{ws_manager.current_file}" alt="Selected file">'

    return template.replace("{{content}}", content)
