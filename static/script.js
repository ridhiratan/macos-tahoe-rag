const chatContainer = document.getElementById('chatContainer');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');

let conversationHistory = [];

// Map filenames to readable titles
const sourceNames = {
    'announcement.txt': 'WWDC 2025 Announcement',
    'release_announcement.txt': 'Release Announcement',
    'release_notes_26.txt': 'Developer Release Notes',
    'release_notes_26_1.txt': 'Release Notes 26.1',
    'release_notes_26_2.txt': 'Release Notes 26.2',
    'whats_new_updates.txt': 'What\'s New in Updates',
    'whats_new_tahoe_guide.txt': 'macOS Tahoe Guide',
    'whats_new_macos26.txt': 'What\'s New in macOS 26',
    'compatible_computers.txt': 'Compatible Computers',
    'enterprise_features.txt': 'Enterprise Features',
    'how_to_upgrade.txt': 'How to Upgrade',
    'macos_main.txt': 'macOS Tahoe Overview',
    'battery_drain_fix.txt': 'Battery Troubleshooting',
    'battery_settings.txt': 'Battery Settings',
    'battery_condition.txt': 'Battery Condition',
    'battery_not_charging.txt': 'Battery Not Charging',
    'startup_issues.txt': 'Startup Issues',
    'diagnose_problems.txt': 'Diagnose Problems',
    'system_settings.txt': 'System Settings',
    'security_content.txt': 'Security Content',
    'storage_mac.txt': 'Storage Management',
    'slow_mac.txt': 'Slow Mac Fixes',
    'wifi_issues.txt': 'Wi-Fi Issues',
    'software_update.txt': 'Software Updates',
    'time_machine.txt': 'Time Machine Backup'
};

function getSourceTitle(filename) {
    return sourceNames[filename] || filename.replace('.txt', '').replace(/_/g, ' ');
}

function addMessage(content, role, sources = []) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const formattedContent = role === 'assistant' ? formatResponse(content) : escapeHtml(content);
    let html = `<div class="message-content">${formattedContent}</div>`;

    // Add collapsible sources for assistant messages
    if (role === 'assistant' && sources && sources.length > 0) {
        const sourceItems = sources.map(s => `<div class="source-item">▸ ${getSourceTitle(s)}</div>`).join('');
        html += `
            <details class="sources-dropdown">
                <summary>Sources (${sources.length})</summary>
                <div class="sources-list">${sourceItems}</div>
            </details>
        `;
    }

    messageDiv.innerHTML = html;
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

function formatResponse(text) {
    // Escape HTML first
    let formatted = escapeHtml(text);
    // Convert line breaks to <br>
    formatted = formatted.replace(/\n\n/g, '</p><p>');
    formatted = formatted.replace(/\n/g, '<br>');
    // Wrap in paragraph
    formatted = '<p>' + formatted + '</p>';
    return formatted;
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
        addMessage(data.response, 'assistant', data.sources || []);

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
