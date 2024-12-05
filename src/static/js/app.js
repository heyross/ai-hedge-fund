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

console.log('WebSocket URL:', WS_URL);  // Debug log

// System State
let isRunning = false;

// Connect to WebSocket server
function connectWebSocket() {
    try {
        console.log('Attempting WebSocket connection...');
        ws = new WebSocket(WS_URL);
        
        ws.onopen = () => {
            console.log('WebSocket connection SUCCESSFULLY established');
            updateConnectionStatus(true);
            
            // Send a test message to verify connection
            ws.send(JSON.stringify({
                type: 'test_connection',
                message: 'Frontend WebSocket connection verified'
            }));
        };
        
        ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                console.log('RECEIVED WebSocket message:', message);
                handleMessage(message);
            } catch (parseError) {
                console.error('CRITICAL: Error parsing WebSocket message:', parseError);
                console.error('Raw received data:', event.data);
            }
        };
        
        ws.onclose = (event) => {
            console.warn('WebSocket connection CLOSED', event);
            updateConnectionStatus(false);
            setTimeout(connectWebSocket, 5000);  // Increased reconnection delay
        };

        ws.onerror = (error) => {
            console.error('CRITICAL WebSocket error:', error);
            updateConnectionStatus(false);
        };
    } catch (connectionError) {
        console.error('CRITICAL WebSocket connection ERROR:', connectionError);
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
    const { role, thought, timestamp } = message;
    
    // Update individual agent thought box
    updateAgentThought(role, thought);
    
    // Optionally add to main chat if it's a significant insight
    if (thought && thought.length > 50) {
        addGroupMessage({
            sender: `${role.replace('_', ' ').toUpperCase()} Agent`,
            content: thought,
            timestamp: timestamp,
            category: 'agent_thought'
        });
    }
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

// Agent Thought Management
const agentThoughtContainers = {
    'market_analyst': document.getElementById('market-analyst-thought'),
    'trading_strategist': document.getElementById('trading-strategist-thought'),
    'risk_manager': document.getElementById('risk-manager-thought')
};

function updateAgentThought(agentRole, thoughtContent) {
    if (agentThoughtContainers[agentRole]) {
        const thoughtContainer = agentThoughtContainers[agentRole];
        
        // Create a new thought element
        const thoughtElement = document.createElement('div');
        thoughtElement.classList.add('agent-thought');
        thoughtElement.innerHTML = `
            <span class="thought-timestamp">${new Date().toLocaleTimeString()}</span>
            <p>${escapeHtml(thoughtContent)}</p>
        `;
        
        // Add animation and limit number of thoughts
        thoughtElement.classList.add('fade-in');
        thoughtContainer.appendChild(thoughtElement);
        
        // Limit to last 5 thoughts
        while (thoughtContainer.children.length > 6) {
            thoughtContainer.removeChild(thoughtContainer.children[1]);
        }
    }
}

// Utility function to escape HTML to prevent XSS
function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
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

    // Check WebSocket connection
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.error('WebSocket is not connected');
        alert('Unable to send message. WebSocket is disconnected.');
        return;
    }

    // Immediately add message to local chat
    addGroupMessage({
        sender: 'You',
        content: content,
        timestamp: new Date().toISOString(),
        category: 'user'
    });

    // Send message via WebSocket
    try {
        ws.send(JSON.stringify({
            type: 'user_message',
            content: content
        }));

        chatInput.value = '';
    } catch (error) {
        console.error('Error sending WebSocket message:', error);
        alert('Failed to send message. Please try again.');
    }
}

sendButton.addEventListener('click', sendMessage);

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Loaded. Initializing WebSocket connection...');
    connectWebSocket();
});
