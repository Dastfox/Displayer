# File Display Server

A FastAPI-based web server that provides real-time file viewing and management capabilities with WebSocket support for
synchronized displays across multiple clients.

## Features

- 🔄 Real-time synchronization across multiple clients via WebSockets
- 📁 Dynamic file structure navigation
- 🖼️ Background management system
- 🔗 Unique URL generation for file sharing
- 📱 Mobile-friendly interface
- 📔 Toggleable journal interface
- 🗂️ Organized file categorization and display

## Setup

### Prerequisites

- Python 3.11 or higher
- Poetry package manager

### Package Dependencies

```toml
fastapi = { extras = ["standard"], version = "^0.115.2" }
python-multipart = "^0.0.12"
aiofiles = "^24.1.0"
jinja2 = "^3.1.4"
pydantic-settings = "^2.6.0"
```

### Installation

1. Install Poetry (if not already installed):

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

2. Clone the repository

3. Install dependencies using Poetry:

```bash
# Navigate to project directory
cd displayer

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### Running the Server

Inside the Poetry virtual environment:

```bash
python main.py
```

Or using Poetry directly:

```bash
poetry run python main.py
```

The server will start and display a URL for local network access:

```
🌐 Access from your phone using: https://<your-ip>:<port>
```

### Managing Dependencies

Add a new dependency:

```bash
poetry add package-name
```

Remove a dependency:

```bash
poetry remove package-name
```

Update dependencies:

```bash
poetry update
```

Export dependencies to requirements.txt:

```bash
poetry export -f requirements.txt --output requirements.txt
```

## Project Structure

```
├── pyproject.toml         # Poetry configuration and dependencies
├── main.py               # Application entry point
├── config.py             # Configuration settings
├── service/
│   └── file_service.py   # File handling services
├── routes/
│   ├── pages.py         # Page routing and rendering
│   └── websocket.py     # WebSocket endpoint handling
├── models/
│   └── websocket.py     # WebSocket manager
└── templates/           # HTML templates
```

## Key Components

### FileService

Handles all file-related operations:

- File structure scanning
- File content retrieval
- File verification
- URL generation

### WebSocketManager

Manages real-time communication:

- Client connections
- State synchronization
- Background management
- Journal button state management

### Routes

#### Pages

- `/`: Home page
- `/first`: Display first available HTML file
- `/manager`: File management interface
- `/display/{unique_id}`: Display selected file
- `/select`: File selection endpoint
- `/select-background`: Background selection endpoint

#### WebSocket

- `/ws/{client_type}`: WebSocket connection endpoint

## Features In Detail

### File Management

- Dynamic file structure scanning
- Excluded directories support
- File type detection
- Unique URL generation for sharing

### Real-time Synchronization

- Connected clients receive updates simultaneously
- Background changes sync across all clients
- Journal button state syncs across sessions

### Background Management

- Background selection and clearing
- Real-time background updates across clients
- Separate background section in manager interface

### Journal Interface

- Toggleable journal button
- State persistence across sessions
- Synchronized visibility across clients

## Security Features

- File path verification
- URL encoding/decoding handling
- Excluded directory protection
- Secure dependency management through Poetry

## Notes

- The system uses a singleton pattern for WebSocket management
- Files in the `unreachable` directory are excluded by default
- Supports HTML and image file display
- Generates unique URLs for file sharing
- Uses Poetry for reproducible dependency management

## Contributing

When contributing to this project:

1. Keep the WebSocket manager singleton pattern
2. Follow the established logging patterns
3. Maintain the file structure organization
4. Test real-time synchronization features
5. Use Poetry for dependency management
6. Update pyproject.toml when adding new dependencies

## Development

### Poetry Commands

```bash
# Update lock file
poetry lock

# Show dependency tree
poetry show --tree

# Run tests (if implemented)
poetry run pytest

# Build project
poetry build
```

## Error Handling

The system includes comprehensive error handling for:

- File not found scenarios
- WebSocket disconnections
- Invalid file paths
- Client connection issues
- Dependency conflicts through Poetry