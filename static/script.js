const chatContainer = document.getElementById('chatContainer');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');

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

// Map filenames to source URLs
const sourceUrls = {
    'announcement.txt': 'https://www.apple.com/newsroom/2025/06/macos-tahoe-26-makes-the-mac-more-capable-productive-and-intelligent-than-ever/',
    'release_announcement.txt': 'https://www.apple.com/newsroom/2025/09/new-versions-of-apples-software-platforms-are-available-today/',
    'release_notes_26.txt': 'https://developer.apple.com/documentation/macos-release-notes/macos-26-release-notes',
    'release_notes.txt': 'https://developer.apple.com/documentation/macos-release-notes/macos-26-release-notes',
    'release_notes_26_1.txt': 'https://developer.apple.com/documentation/macos-release-notes/macos-26_1-release-notes',
    'release_notes_26_2.txt': 'https://developer.apple.com/documentation/macos-release-notes/macos-26_2-release-notes',
    'whats_new_updates.txt': 'https://support.apple.com/en-us/122868',
    'whats_new_tahoe_guide.txt': 'https://support.apple.com/guide/mac-help/whats-new-in-macos-tahoe-apd07d671600/mac',
    'whats_new_macos26.txt': 'https://developer.apple.com/documentation/macos-release-notes/macos-26-release-notes#Whats-New',
    'compatible_computers.txt': 'https://support.apple.com/en-us/122867',
    'enterprise_features.txt': 'https://support.apple.com/en-us/124963',
    'how_to_upgrade.txt': 'https://support.apple.com/en-us/122727',
    'macos_main.txt': 'https://www.apple.com/macos/',
    'battery_drain_fix.txt': 'https://support.apple.com/guide/mac-help/if-your-battery-runs-out-of-charge-quickly-mh27540/mac',
    'battery_settings.txt': 'https://support.apple.com/guide/mac-help/change-battery-settings-mchlfc3b7879/mac',
    'battery_condition.txt': 'https://support.apple.com/guide/mac-help/check-the-condition-of-your-computers-battery-mh20865/mac',
    'battery_not_charging.txt': 'https://support.apple.com/guide/mac-help/if-your-battery-status-is-not-charging-mh20876/mac',
    'startup_issues.txt': 'https://support.apple.com/en-us/123922',
    'diagnose_problems.txt': 'https://support.apple.com/guide/mac-help/diagnose-problems-mh35727/mac',
    'system_settings.txt': 'https://support.apple.com/guide/mac-help/change-system-settings-mh15217/mac',
    'security_content.txt': 'https://support.apple.com/en-us/125110',
    'storage_mac.txt': 'https://support.apple.com/guide/mac-help/free-up-storage-space-on-your-mac-mchl43d7b4e0/mac',
    'slow_mac.txt': 'https://support.apple.com/guide/mac-help/if-your-mac-runs-slowly-mh27606/mac',
    'wifi_issues.txt': 'https://support.apple.com/guide/mac-help/if-your-mac-doesnt-connect-to-the-internet-mchlp1498/mac',
    'software_update.txt': 'https://support.apple.com/guide/mac-help/get-macos-updates-mchlpx1065/mac',
    'time_machine.txt': 'https://support.apple.com/guide/mac-help/back-up-your-mac-with-time-machine-mh35860/mac'
};

function getSourceTitle(filename) {
    return sourceNames[filename] || filename.replace('.txt', '').replace(/_/g, ' ');
}

function getSourceUrl(filename) {
    return sourceUrls[filename] || null;
}

function addMessage(content, role, sources = [], webSources = [], sourceType = 'rag') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const formattedContent = role === 'assistant' ? formatResponse(content) : escapeHtml(content);
    let html = `<div class="message-content">${formattedContent}</div>`;

    if (role === 'assistant') {
        // RAG sources
        if (sourceType === 'rag' && sources && sources.length > 0) {
            const sourceItems = sources.map(s => {
                const title = getSourceTitle(s);
                const url = getSourceUrl(s);
                if (url) {
                    return `<div class="source-item"><a href="${url}" target="_blank" rel="noopener noreferrer">▸ ${title}</a></div>`;
                }
                return `<div class="source-item">▸ ${title}</div>`;
            }).join('');
            html += `
                <details class="sources-dropdown">
                    <summary>Sources (${sources.length})</summary>
                    <div class="sources-list">${sourceItems}</div>
                </details>
            `;
        }

        // Web sources
        if (sourceType === 'web' && webSources && webSources.length > 0) {
            const webItems = webSources.map(s =>
                `<div class="source-item"><a href="${escapeHtml(s.url)}" target="_blank" rel="noopener noreferrer">▸ ${escapeHtml(s.title)}</a></div>`
            ).join('');
            html += `
                <details class="sources-dropdown web-sources" open>
                    <summary>Web Sources (${webSources.length})</summary>
                    <div class="sources-list">${webItems}</div>
                </details>
            `;
        }
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
        addMessage(data.response, 'assistant', data.sources || [], data.web_sources || [], data.source_type || 'rag');

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

clearBtn.addEventListener('click', () => {
    conversationHistory = [];
    chatContainer.innerHTML = `
        <div class="message assistant">
            <div class="message-content">
                Hello! I'm your macOS Tahoe assistant. Ask me anything about macOS 26 - features, settings, compatibility, and more.
            </div>
        </div>
    `;
    messageInput.focus();
});
