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
        handleMessage(message);
    };
    
    ws.onclose = () => {
        console.log('Disconnected from server');
        if (isRunning) {
            // Attempt to reconnect
            setTimeout(connectWebSocket, 1000);
        }
    };
}

// Message Handlers
function handleMessage(message) {
    switch (message.type) {
        case 'system_status':
            updateSystemStatus(message.data);
            break;
        case 'group_message':
            addGroupMessage(message.data);
            break;
        case 'private_message':
            addPrivateMessage(message.data);
            break;
        case 'agent_status':
            updateAgentStatus(message.data);
            break;
        case 'portfolio_update':
            updatePortfolioValue(message.data);
            break;
    }
}

// UI Updates
function updateSystemStatus(status) {
    isRunning = status.running;
    statusIndicator.classList.toggle('running', isRunning);
    statusText.textContent = isRunning ? 'System Running' : 'System Stopped';
    startButton.disabled = isRunning;
    stopButton.disabled = !isRunning;
}

function addGroupMessage(message) {
    const messageElement = createMessageElement(message);
    centralChat.appendChild(messageElement);
    centralChat.scrollTop = centralChat.scrollHeight;
}

function addPrivateMessage(message) {
    const agentRoom = document.querySelector(`.agent-room.${message.agent.toLowerCase()} .private-chat`);
    const messageElement = createMessageElement(message);
    agentRoom.appendChild(messageElement);
    agentRoom.scrollTop = agentRoom.scrollHeight;
}

function updateAgentStatus(status) {
    const agentStatusElement = document.querySelector(`.agent-room.${status.agent.toLowerCase()} .agent-status .status`);
    agentStatusElement.textContent = status.status;
}

function updatePortfolioValue(value) {
    document.querySelector('.portfolio-value .value').textContent = formatCurrency(value);
}

// Helper Functions
function createMessageElement(message) {
    const div = document.createElement('div');
    div.className = 'message';
    
    div.innerHTML = `
        <div class="message-header">
            <span class="agent-name">${message.sender}</span>
            <span class="timestamp">${formatTimestamp(message.timestamp)}</span>
        </div>
        <div class="message-content">${message.content}</div>
        <div class="message-footer">
            <span class="message-type">${message.category}</span>
        </div>
    `;
    
    return div;
}

function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleTimeString();
}

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

// Event Listeners
startButton.addEventListener('click', () => {
    if (ws) {
        ws.send(JSON.stringify({
            type: 'command',
            action: 'start'
        }));
    }
});

stopButton.addEventListener('click', () => {
    if (ws) {
        ws.send(JSON.stringify({
            type: 'command',
            action: 'stop'
        }));
    }
});

sendButton.addEventListener('click', () => {
    if (ws && chatInput.value.trim()) {
        ws.send(JSON.stringify({
            type: 'user_message',
            content: chatInput.value.trim()
        }));
        chatInput.value = '';
    }
});

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendButton.click();
    }
});

// Initialize
connectWebSocket();
