import uuid
from pathlib import Path
from urllib.parse import unquote

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# List to hold connected WebSocket clients
clients = []
# Variable to store the currently selected file and its unique URL
current_file = None
current_file_url = None


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
        <html>
            <head>
                <title>File Sharing System</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #1c2e4a;
                        background-image: url("/static/Backgrounds/Palais.png");
                        background-size: 100% auto; 
                        background-repeat: no-repeat; 
                        background-position: center; 
                        text-align: center;
                        padding: 20px;
                        margin: 0;
                        color: white;
                    }
                    h1 {
                        font-size: 24px;
                        margin-bottom: 20px;
                    }
                    a {
                        display: inline-block;
                        text-decoration: none;
                        color: #ffffff;
                        font-size: 18px;
                        background-color: #007bff;
                        padding: 12px 24px;
                        border-radius: 8px;
                        transition: background-color 0.3s;
                    }
                    a:hover {
                        background-color: #0056b3;
                    }
                    @media (max-width: 600px) {
                        body {
                            padding: 15px;
                        }
                        h1 {
                            font-size: 20px;
                        }
                        a {
                            font-size: 16px;
                            padding: 10px 20px;
                        }
                    }
                </style>
            </head>
            <body>
                <h1>Vampire: La Masquarade</h1>
                <h2>Paris at night</h2>
                <script>
                    const ws = new WebSocket("ws://" + window.location.host + "/ws/home");
                    ws.onmessage = (event) => {
                        if (window.location.pathname !== event.data) {
                            window.location.href = event.data;
                        }
                    };
                </script>
            </body>
        </html>
    """


@app.get("/manager", response_class=HTMLResponse)
async def manager(request: Request):
    static_dir = Path("static")
    files = []
    for file_path in static_dir.rglob("*"):
        if file_path.is_file():
            rel_path = file_path.relative_to(static_dir)
            files.append(str(rel_path))
    # Use encodeURIComponent in JavaScript for proper URL encoding
    buttons = "".join(f"<button class='file-button' onclick=\"selectFile('{file}')\">{file}</button>" for file in files)
    return f"""
        <html>
            <head>
                <title>File Manager</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #1c2e4a;
                        text-align: center;
                        padding: 20px;
                        margin: 0;
                        color: white;
                    }}
                    h1 {{
                        color: white;
                        font-size: 24px;
                        margin-bottom: 30px;
                    }}
                    .files-container {{
                        max-width: 800px;
                        margin: 0 auto;
                        display: grid;
                        gap: 10px;
                        padding: 10px;
                    }}
                    .file-button {{
                        width: 100%;
                        padding: 15px;
                        font-size: 16px;
                        color: white;
                        background-color: #2c3e60;
                        border: 1px solid #34495e;
                        border-radius: 8px;
                        cursor: pointer;
                        transition: background-color 0.3s, transform 0.2s;
                        word-break: break-all;
                    }}
                    .file-button:hover {{
                        background-color: #34495e;
                        transform: translateY(-2px);
                    }}
                    .file-button:active {{
                        transform: translateY(0);
                    }}
                    #confirmation {{
                        margin-top: 20px;
                        color: #2ecc71;
                        padding: 10px;
                        border-radius: 5px;
                        font-weight: bold;
                    }}
                    @media (max-width: 600px) {{
                        body {{
                            padding: 10px;
                        }}
                        h1 {{
                            font-size: 20px;
                            margin-bottom: 20px;
                        }}
                        .file-button {{
                            padding: 12px;
                            font-size: 14px;
                        }}
                    }}
                </style>
            </head>
            <body>
                <h1>File Manager</h1>
                <div class="files-container">
                    {buttons}
                </div>
                <p id="confirmation"></p>
                <script>
                    const ws = new WebSocket("ws://" + window.location.host + "/ws/manager");
                    function selectFile(file) {{
                        // Properly encode the file name for the URL
                        const encodedFile = encodeURIComponent(file);
                        fetch('/select?file=' + encodedFile, {{ method: 'GET' }})
                            .then(response => response.json())
                            .then(data => {{
                                document.getElementById('confirmation').innerText = data.message;
                                setTimeout(() => {{
                                    document.getElementById('confirmation').innerText = '';
                                }}, 3000);
                            }})
                            .catch(error => {{
                                console.error('Error:', error);
                                document.getElementById('confirmation').innerText = 'Error selecting file';
                            }});
                    }}
                </script>
            </body>
        </html>
    """


@app.get("/select")
async def select_file(file: str):
    global current_file, current_file_url

    # Decode the URL-encoded filename
    decoded_file = unquote(file)

    # Verify the file exists in the static directory
    file_path = Path("static") / decoded_file
    if not file_path.exists() or not file_path.is_file():
        return JSONResponse(
            status_code=404,
            content={"message": f"File '{decoded_file}' not found"}
        )

    # Generate a unique link for the selected file
    unique_id = str(uuid.uuid4())
    current_file = decoded_file
    current_file_url = f"/display/{unique_id}"

    # Notify all clients except those connected to /manager
    disconnected_clients = []
    for client in clients:
        try:
            if client.path != "/ws/manager":
                await client.send_text(current_file_url)
        except WebSocketDisconnect:
            disconnected_clients.append(client)

    # Remove disconnected clients
    for client in disconnected_clients:
        clients.remove(client)

    return JSONResponse(content={"message": f"File '{decoded_file}' selected. All clients updated."})


@app.get("/display/{unique_id}", response_class=HTMLResponse)
async def display(unique_id: str):
    if current_file and current_file_url and current_file_url.endswith(unique_id):
        content_html = "<h1>Waiting for the selected file...</h1>"
        extension = current_file.split('.').pop().lower()
        if extension == 'html':
            with open(f'static/{current_file}', 'r') as f:
                content_html = f.read()
        else:
            content_html = f'<img src="/static/{current_file}" alt="Selected file">'
        return HTMLResponse(f"""
            <html>
                <head>
                    <title>Display File</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #1c2e4a;
                            background-image: url("/static/Backgrounds/Palais.png");
                            background-size: 100% auto; 
                            background-repeat: no-repeat; 
                            background-position: center; 
                            margin: 0;
                            padding: 20px;
                            min-height: 100vh;
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            justify-content: center;
                        }}
                        #content {{
                            max-width: 1200px;
                            margin: 0 auto;
                        }}
                        #content img {{
                            width: 100%;
                            max-height: 90vh;
                            height: auto;
                            border-radius: 8px;
                            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                        }}
                        @media (max-width: 600px) {{
                            body {{
                                padding: 10px;
                            }}
                        }}
                    </style>
                </head>
                <body>
                    <div id="content">{content_html}</div>
                    <script>
                        const ws = new WebSocket("ws://" + window.location.host + "/ws/display");
                        ws.onmessage = (event) => {{
                            if (window.location.pathname !== event.data) {{
                                window.location.href = event.data;
                            }}
                        }};
                    </script>
                </body>
            </html>
        """)
    return RedirectResponse(url="/")


@app.websocket("/ws/{client_type}")
async def websocket_endpoint(websocket: WebSocket, client_type: str):
    await websocket.accept()
    websocket.path = f"/ws/{client_type}"
    clients.append(websocket)
    try:
        if current_file_url and client_type != "manager":
            await websocket.send_text(current_file_url)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
