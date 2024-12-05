// DOM Elements
const startButton = document.getElementById('startSystem');
const stopButton = document.getElementById('stopSystem');
const statusIndicator = document.querySelector('.status-indicator');
const statusText = document.querySelector('.status-text');
const centralChat = document.querySelector('.chat-messages');
const chatInput = document.querySelector('.chat-input textarea');
const sendButton = document.querySelector('.chat-input button');

// WebSocket Connection
let ws = null;

// System State
let isRunning = false;

// Connect to WebSocket server
function connectWebSocket() {
    ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
        console.log('Connected to server');
    };
    
    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        console.log('Received message:', message);  // Debug log
        handleMessage(message);
    };
    
    ws.onclose = () => {
        console.log('Disconnected from server');
        setTimeout(connectWebSocket, 1000);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

// Message Handlers
function handleMessage(message) {
    console.log('Handling message:', message);  // Debug log
    switch (message.type) {
        case 'system_status':
            updateSystemStatus(message.data);
            break;
        case 'system_message':
            addGroupMessage({
                sender: 'System',
                content: message.content,
                timestamp: new Date().toISOString(),
                category: 'system'
            });
            break;
        case 'user_message':
            addGroupMessage({
                sender: 'You',
                content: message.content,
                timestamp: new Date().toISOString(),
                category: 'user'
            });
            break;
        case 'agent_message':
            addGroupMessage({
                sender: message.sender,
                content: message.content,
                timestamp: message.timestamp,
                category: 'agent'
            });
            break;
        default:
            console.log('Unknown message type:', message.type);
    }
}

// UI Updates
function updateSystemStatus(status) {
    isRunning = status.running;
    statusIndicator.classList.toggle('active', isRunning);
    statusText.textContent = isRunning ? 'System Running' : 'System Stopped';
    startButton.disabled = isRunning;
    stopButton.disabled = !isRunning;
}

function addGroupMessage(message) {
    console.log('Adding group message:', message);  // Debug log
    const messageElement = createMessageElement(message);
    centralChat.appendChild(messageElement);
    centralChat.scrollTop = centralChat.scrollHeight;
}

function createMessageElement(message) {
    const div = document.createElement('div');
    div.className = `message ${message.category}`;
    
    div.innerHTML = `
        <div class="message-header">
            <span class="sender">${message.sender}</span>
            <span class="timestamp">${formatTimestamp(message.timestamp)}</span>
        </div>
        <div class="message-content">${message.content}</div>
    `;
    
    return div;
}

function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleTimeString();
}

// Event Listeners
startButton.addEventListener('click', () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        console.log('Sending start command');  // Debug log
        ws.send(JSON.stringify({
            type: 'command',
            action: 'start'
        }));
    }
});

stopButton.addEventListener('click', () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        console.log('Sending stop command');  // Debug log
        ws.send(JSON.stringify({
            type: 'command',
            action: 'stop'
        }));
    }
});

function sendMessage() {
    const content = chatInput.value.trim();
    if (!content) return;

    // Don't add message locally - wait for server echo
    ws.send(JSON.stringify({
        type: 'user_message',
        content: content
    }));

    chatInput.value = '';
}

sendButton.addEventListener('click', sendMessage);

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Initialize
connectWebSocket();
