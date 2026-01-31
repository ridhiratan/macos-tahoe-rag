const chatContainer = document.getElementById('chatContainer');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');

let conversationHistory = [];

function addMessage(content, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `<div class="message-content">${escapeHtml(content)}</div>`;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function addTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="typing">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function sendMessage(message) {
    sendBtn.disabled = true;
    addMessage(message, 'user');
    addTypingIndicator();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                history: conversationHistory
            })
        });

        removeTypingIndicator();

        if (!response.ok) {
            throw new Error('Failed to get response');
        }

        const data = await response.json();
        addMessage(data.response, 'assistant');

        // Update history
        conversationHistory.push({ role: 'user', content: message });
        conversationHistory.push({ role: 'assistant', content: data.response });

        // Keep history manageable (last 10 exchanges)
        if (conversationHistory.length > 20) {
            conversationHistory = conversationHistory.slice(-20);
        }
    } catch (error) {
        removeTypingIndicator();
        addMessage('Sorry, something went wrong. Please try again.', 'assistant');
        console.error(error);
    }

    sendBtn.disabled = false;
    messageInput.focus();
}

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (message) {
        messageInput.value = '';
        sendMessage(message);
    }
});
