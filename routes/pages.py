# app/routes/pages.py
import logging
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from service.file_service import FileService
from models.websocket import WebSocketManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()
ws_manager = WebSocketManager()

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"


def get_template(template_name: str) -> str:
    """Read and return the content of a template file"""
    template_path = TEMPLATE_DIR / template_name
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


@router.get("/first", response_class=HTMLResponse)
async def first_html():
    """Display the first HTML file if it exists"""
    file_structure = FileService.get_file_structure()

    # Find first HTML file
    first_html = None
    for section, items in file_structure.items():
        if isinstance(items, dict):
            for filename, filepath in items.items():
                if filename.lower().endswith('.html'):
                    first_html = filepath
                    break
        if first_html:
            break

    if not first_html:
        return RedirectResponse(url="/")

    template = get_template('display_journal.html')
    content = FileService.get_file_content(first_html)
    return template.replace("{{content}}", content)

@router.get("/", response_class=HTMLResponse)
async def home():
    return get_template('home.html')


@router.get("/toggle-journal-button")
async def toggle_journal_button():
    """Toggle the visibility of the journal button"""
    ws_manager.show_journal_button = not ws_manager.show_journal_button
    logger.info(f"Journal button visibility toggled to: {ws_manager.show_journal_button}")

    # Broadcast the new state to all clients
    await ws_manager.broadcast_journal_state()

    return JSONResponse(
        content={
            "show_journal_button": ws_manager.show_journal_button,
            "message": "Journal button state updated"
        }
    )
@router.get("/manager", response_class=HTMLResponse)
async def manager(request: Request):
    file_structure = FileService.get_file_structure()
    template = get_template('manager.html')

    button_section_begin = '<div class="section files-container">'
    button_section_end = '</div>'

    def create_section_html(section_name: str, items: dict) -> str:
        # Convert section name to title format
        section_title = section_name.replace('_', ' ').title()

        html = f'<div class="section">'
        html += f'<h2 class="section-title">{section_title}</h2>'

        # Sort and process files
        files = []
        for file_name in sorted(items.keys()):
            file_path = items[file_name]
            # Get clean name without extension and path
            clean_name = Path(file_name).stem
            # Convert to title case and replace underscores with spaces
            display_name = clean_name.replace('_', ' ').title()
            files.append((display_name, file_path, file_name))

        # Add file buttons
        for display_name, file_path, original_name in files:
            html += f'<button class="file-button" data-file="{file_path}" '
            html += f'onclick="selectFile(\'{file_path}\')" '
            html += f'title="{original_name}">{display_name}</button>'

        html += '</div>'
        return html

    # Create sections HTML
    sections_html = ""
    for section_name, items in sorted(file_structure.items()):
        if isinstance(items, dict):  # Only process directories
            sections_html += create_section_html(section_name, items)

    # add begin and end
    sections_html = button_section_begin + sections_html + button_section_end
    # Add journal button toggle and clear selection button
    journal_toggle = '''
        <div class="button-controls">
            <button class="file-button journal-toggle" 
                    onclick="toggleJournalButton()"
                    data-active="{}">
                {} Journal Button
            </button>
        </div>
    '''.format(
        str(ws_manager.show_journal_button).lower(),
        "Hide" if ws_manager.show_journal_button else "Show"
    )
    sections_html += journal_toggle
    sections_html += '<button class="file-button clear-button" onclick="selectFile()">Clear Selection</button>'



    return template.replace("{{buttons}}", sections_html)


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