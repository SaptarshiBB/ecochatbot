const chatbox = document.getElementById('chatbox');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const themeSwitch = document.getElementById('themeSwitch');
const newChatBtn = document.getElementById('newChatBtn');
const recentChats = document.getElementById('recentChats');
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebarToggle');
const clearChatsBtn = document.getElementById('clearChatsBtn');
const body = document.body;

let currentSessionId = 'default';
let touchStartX = 0;

// Theme management
function setTheme(theme) {
    body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    themeSwitch.checked = theme === 'dark';
}

// Initialize theme
const savedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
setTheme(savedTheme);

// Format timestamp
function formatTimestamp(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' ' +
           date.toLocaleDateString([], { month: 'short', day: 'numeric' });
}

// Display message
function displayMessage(message, sender, timestamp, isNew = true) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender === 'user' ? 'user-message' : 'bot-message'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'markdown-content';
    contentDiv.innerHTML = marked.parse(message);
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'timestamp';
    timeSpan.textContent = formatTimestamp(timestamp);
    
    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timeSpan);
    
    chatbox.appendChild(messageDiv);
    if (isNew) {
        chatbox.scrollTop = chatbox.scrollHeight;
    }
}

// Display typing indicator
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
    chatbox.appendChild(typingDiv);
    chatbox.scrollTop = chatbox.scrollHeight;
    return typingDiv;
}

// Remove typing indicator
function removeTypingIndicator(typingDiv) {
    if (typingDiv) typingDiv.remove();
}

// Send message
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    userInput.value = '';
    sendButton.disabled = true;

    displayMessage(message, 'user', new Date().toISOString());
    const typingDiv = showTypingIndicator();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSessionId, message })
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();
        removeTypingIndicator(typingDiv);

        if (data.error) {
            displayMessage(data.error, 'bot', new Date().toISOString());
        } else {
            displayMessage(data.response, 'bot', new Date().toISOString());
            await loadRecentChats();
            const chatItem = recentChats.querySelector(`[data-session-id="${currentSessionId}"]`);
            if (chatItem) chatItem.textContent = data.title;
        }
    } catch (error) {
        console.error('Error sending message:', error);
        removeTypingIndicator(typingDiv);
        displayMessage('Error communicating with server', 'bot', new Date().toISOString());
    } finally {
        sendButton.disabled = false;
        userInput.focus();
    }
}

// Load recent chats
async function loadRecentChats() {
    try {
        const response = await fetch('/recent_chats');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const chats = await response.json();
        recentChats.innerHTML = '';

        chats.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).forEach(chat => {
            const chatItem = document.createElement('div');
            chatItem.className = `recent-chat-item ${chat.session_id === currentSessionId ? 'active' : ''}`;
            chatItem.dataset.sessionId = chat.session_id;
            chatItem.innerHTML = `<span class="material-icons">chat</span>${chat.title}`;
            chatItem.addEventListener('click', () => loadChatSession(chat.session_id));
            recentChats.appendChild(chatItem);
        });
    } catch (error) {
        console.error('Error loading recent chats:', error);
    }
}

// Load specific chat session
async function loadChatSession(sessionId) {
    currentSessionId = sessionId;
    chatbox.innerHTML = '';
    
    try {
        const response = await fetch(`/chat/${sessionId}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const session = await response.json();
        
        if (session.error) {
            displayMessage(session.error, 'bot', new Date().toISOString(), false);
        } else {
            session.messages.forEach(msg => {
                displayMessage(msg.message, msg.sender, msg.timestamp, false);
            });
        }
        
        document.querySelectorAll('.recent-chat-item').forEach(item => {
            item.classList.toggle('active', item.dataset.sessionId === sessionId);
        });
        
        chatbox.scrollTop = chatbox.scrollHeight;
        sidebar.classList.remove('open');
    } catch (error) {
        console.error('Error loading chat session:', error);
        displayMessage('Error loading chat session', 'bot', new Date().toISOString(), false);
    }
}

// Create new chat
async function createNewChat() {
    try {
        const response = await fetch('/new_chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        currentSessionId = data.session_id;
        chatbox.innerHTML = '';

        data.messages.forEach(msg => {
            displayMessage(msg.message, msg.sender, msg.timestamp, false);
        });

        await loadRecentChats();
        loadChatSession(currentSessionId);
    } catch (error) {
        console.error('Error creating new chat:', error);
        displayMessage('Error creating new chat', 'bot', new Date().toISOString());
    }
}

// Clear all chats
async function clearAllChats() {
    try {
        const response = await fetch('/clear-chats', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        if (data.message) {
            currentSessionId = 'default';
            chatbox.innerHTML = '';
            await loadChatSession(currentSessionId);
            await loadRecentChats();
            displayMessage('All chats have been cleared. Starting fresh with the default session.', 'bot', new Date().toISOString());
            sidebar.classList.remove('open');
        } else if (data.error) {
            displayMessage(data.error, 'bot', new Date().toISOString());
        }
    } catch (error) {
        console.error('Error clearing chats:', error);
        displayMessage('Error clearing chats', 'bot', new Date().toISOString());
    }
}

// Toggle sidebar
function toggleSidebar() {
    sidebar.classList.toggle('open');
}

// Event listeners
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !sendButton.disabled) sendMessage();
});

sendButton.addEventListener('click', sendMessage);
newChatBtn.addEventListener('click', createNewChat);
clearChatsBtn.addEventListener('click', clearAllChats);
sidebarToggle.addEventListener('click', toggleSidebar);
themeSwitch.addEventListener('change', () => setTheme(themeSwitch.checked ? 'dark' : 'light'));

// Swipe handling
sidebar.addEventListener('touchstart', (e) => {
    touchStartX = e.touches[0].clientX;
});

sidebar.addEventListener('touchend', (e) => {
    const touchEndX = e.changedTouches[0].clientX;
    if (touchEndX - touchStartX > 50) toggleSidebar();
    if (touchStartX - touchEndX > 50) toggleSidebar();
});

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadRecentChats();
    await loadChatSession(currentSessionId);
    userInput.focus();
});