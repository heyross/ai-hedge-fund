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
const WS_URL = window.location.hostname === 'localhost' 
    ? 'ws://localhost:8000/ws' 
    : `wss://${window.location.host}/ws`;

// System State
let isRunning = false;

// Connect to WebSocket server
function connectWebSocket() {
    try {
        ws = new WebSocket(WS_URL);
        
        ws.onopen = () => {
            console.log('WebSocket connection established');
            updateConnectionStatus(true);
        };
        
        ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                console.log('Received WebSocket message:', message);
                handleMessage(message);
            } catch (parseError) {
                console.error('Error parsing WebSocket message:', parseError);
                console.error('Raw message:', event.data);
            }
        };
        
        ws.onclose = (event) => {
            console.warn('WebSocket connection closed', event);
            updateConnectionStatus(false);
            setTimeout(connectWebSocket, 3000);  // Increased delay
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateConnectionStatus(false);
        };
    } catch (connectionError) {
        console.error('WebSocket connection error:', connectionError);
        updateConnectionStatus(false);
    }
}

// Connection Status Tracking
function updateConnectionStatus(isConnected) {
    const connectionIndicator = document.getElementById('connectionIndicator');
    if (connectionIndicator) {
        connectionIndicator.classList.toggle('connected', isConnected);
        connectionIndicator.title = isConnected 
            ? 'WebSocket Connected' 
            : 'WebSocket Disconnected';
    }
}

// Comprehensive Message Handlers
function handleMessage(message) {
    console.log('Processing message:', message);
    
    // Validate message structure
    if (!message || !message.type) {
        console.warn('Invalid message structure:', message);
        return;
    }
    
    // Expanded message type handling
    switch (message.type) {
        case 'system_status':
            updateSystemStatus(message.data);
            break;
        
        case 'system_message':
            addSystemMessage(message);
            break;
        
        case 'agent_thought':
            handleAgentThought(message);
            break;
        
        case 'agent_status':
            updateAgentStatus(message);
            break;
        
        case 'market_data':
            updateMarketData(message);
            break;
        
        case 'user_message':
        case 'agent_message':
            addGroupMessage({
                sender: message.sender || 'Unknown',
                content: message.content,
                timestamp: message.timestamp || new Date().toISOString(),
                category: message.type.replace('_message', '')
            });
            break;
        
        default:
            console.log('Unhandled message type:', message.type);
    }
}

// New specialized message handlers
function handleAgentThought(message) {
    const agentName = message.sender || 'Agent';
    const privateChat = document.querySelector(`.agent-room.${agentName.toLowerCase()} .private-chat`);
    
    if (privateChat) {
        const thoughtElement = document.createElement('div');
        thoughtElement.className = 'agent-thought';
        thoughtElement.innerHTML = `
            <span class="sender">${agentName}</span>
            <p>${message.content}</p>
        `;
        privateChat.appendChild(thoughtElement);
        privateChat.scrollTop = privateChat.scrollHeight;
    }
    
    // Also add to central chat for transparency
    addGroupMessage({
        sender: agentName,
        content: message.content,
        timestamp: message.timestamp || new Date().toISOString(),
        category: 'agent_thought'
    });
}

function updateAgentStatus(message) {
    const agentStatusElement = document.querySelector(
        `.agent-room.${message.sender.toLowerCase()} .agent-status .status`
    );
    
    if (agentStatusElement) {
        agentStatusElement.textContent = message.content || 'Active';
        agentStatusElement.classList.toggle('active', message.content !== 'Idle');
    }
}

function updateMarketData(message) {
    // Placeholder for market data updates
    console.log('Market Data Update:', message);
    // You could update specific market data displays here
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
