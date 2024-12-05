# AI Hedge Fund Web Interface Design

## Overview
A modern web interface for interacting with multiple AI trading agents, featuring a central group chat and private agent-specific chat rooms.

## Layout Design

### Main Components
1. **Header Bar**
   - System status indicator (Running/Stopped)
   - Start/Stop controls
   - System settings button
   - Current portfolio value display

2. **Central Chat Room**
   - Occupies the center ~60% of the screen
   - Shows inter-agent communications
   - Allows user participation in group discussion
   - Message types:
     - Trading decisions
     - Market analysis
     - Risk assessments
     - Portfolio updates
   - Features:
     - Timestamp for each message
     - Agent identification (name/icon)
     - Message categorization (color-coded by type)
     - Scrollable history

3. **Agent Private Rooms**
   - Surrounding the central chat (grid layout)
   - Individual rooms for each agent:
     - Market Data Agent
     - Quantitative Agent
     - Risk Management Agent
     - Portfolio Management Agent
   - Features:
     - Real-time thought process display
     - Direct communication with user
     - Agent status and current task
     - Key metrics relevant to each agent

### Interactive Elements

1. **System Controls**
   ```html
   <!-- Example control structure -->
   <div class="system-controls">
     <button id="startSystem">Start Trading</button>
     <button id="stopSystem">Stop Trading</button>
     <button id="systemSettings">Settings</button>
   </div>
   ```

2. **Chat Interface**
   ```html
   <!-- Example message structure -->
   <div class="message">
     <div class="message-header">
       <span class="agent-name">Agent Name</span>
       <span class="timestamp">HH:MM:SS</span>
     </div>
     <div class="message-content">Message text</div>
     <div class="message-footer">
       <span class="message-type">Message Category</span>
     </div>
   </div>
   ```

## Color Scheme
- Background: Dark theme (#1E1E1E)
- Text: Light gray (#E0E0E0)
- Accent colors:
  - System status: Green (#4CAF50) / Red (#F44336)
  - Market Data: Blue (#2196F3)
  - Quantitative: Purple (#9C27B0)
  - Risk Management: Orange (#FF9800)
  - Portfolio Management: Teal (#009688)

## Typography
- Main font: 'Inter', sans-serif
- Monospace elements: 'Fira Code', monospace
- Message text: 16px
- Headers: 20px/24px
- System status: 18px

## Responsive Design
- Desktop-first approach
- Breakpoints:
  - Large: 1920px+
  - Medium: 1366px
  - Small: 1024px
- Mobile view: Stacked layout with collapsible agent rooms

## Future Enhancements
1. Trading Controls
   - Asset selection
   - Risk tolerance adjustment
   - Trading strategy parameters

2. Visualization
   - Real-time charts
   - Performance metrics
   - Portfolio composition

3. Agent Configuration
   - Agent parameter tuning
   - Strategy customization
   - Alert thresholds

4. Data Export
   - Chat history
   - Trading history
   - Performance reports
