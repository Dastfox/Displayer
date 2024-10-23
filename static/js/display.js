// Initialize WebSocket connection
const ws = new WebSocket("ws://" + window.location.host + "/ws/display");

// Function to initialize the journal button state
async function initializeJournalButtonState() {
    try {
        const response = await fetch('/get-journal-button-state');
        const data = await response.json();
        const journalButton = document.getElementById('journal-button');
        if (journalButton) {
            journalButton.style.display = data.show_journal_button ? 'block' : 'none';
        }
    } catch (error) {
        console.error('Error fetching initial journal button state:', error);
    }
}

// Function to initialize background if one is set
async function initializeBackground() {
    try {
        const response = await fetch('/select-background');
        const data = await response.json();
        if (data.background) {
            document.body.style.backgroundImage = `url('/static/${data.background}')`;
        }
    } catch (error) {
        console.error('Error fetching initial background state:', error);
    }
}

// Initialize states when page loads
document.addEventListener('DOMContentLoaded', () => {
    initializeJournalButtonState();
    initializeBackground();
});

// WebSocket message handler
ws.onmessage = (event) => {
    const is_object = event.data.startsWith("{");
    console.log("WebSocket message received:", event.data);

    if (!is_object && window.location.pathname !== event.data) {
        window.location.href = event.data;
        return;
    }

    if (is_object) {
        try {
            const data = JSON.parse(event.data);
            console.log("Parsed WebSocket data:", data);

            switch (data.type) {
                case 'journal_state':
                    const journalButton = document.getElementById('journal-button');
                    if (journalButton) {
                        journalButton.style.display = data.show_journal_button ? 'block' : 'none';
                    }
                    break;

                case 'background':
                    if (data.path) {
                        document.body.style.backgroundImage = `url('/static/${data.path}')`;
                    } else {
                        document.body.style.backgroundImage = 'none';
                    }
                    break;

                default:
                    console.log('Unknown message type:', data.type);
            }
        } catch (error) {
            console.error('Error processing WebSocket message:', error);
        }
    }
};

// Handle WebSocket errors
ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

// Handle WebSocket connection close
ws.onclose = (event) => {
    console.log('WebSocket connection closed:', event.code, event.reason);
};