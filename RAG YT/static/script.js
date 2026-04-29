// DOM Elements
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const queryInput = document.getElementById('queryInput');
const sendBtn = document.getElementById('sendBtn');
const chatContainer = document.getElementById('chatContainer');
const clearBtn = document.getElementById('clearBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const docCount = document.getElementById('docCount');
const systemStatus = document.getElementById('systemStatus');

let isInitialized = false;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkStatus();
    setupEventListeners();
    setInterval(checkStatus, 5000); // Check status every 5 seconds
});

// Setup Event Listeners
function setupEventListeners() {
    // Upload area
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    fileInput.addEventListener('change', handleFileSelect);

    // Query
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            sendQuery();
        }
    });

    sendBtn.addEventListener('click', sendQuery);

    // Clear
    clearBtn.addEventListener('click', clearIndex);
}

// File Upload Handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    uploadFiles(files);
}

function handleFileSelect(e) {
    uploadFiles(e.target.files);
}

async function uploadFiles(files) {
    if (files.length === 0) return;

    const formData = new FormData();
    for (let file of files) {
        if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
            formData.append('files', file);
        }
    }

    if (formData.getAll('files').length === 0) {
        showNotification('Please upload .txt files only', 'error');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showNotification(data.message, 'success');
            clearChat();
            addMessage('System', 'Documents have been indexed. You can now ask questions!', 'assistant');
            checkStatus();
        } else {
            showNotification(data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        showNotification('Error uploading files: ' + error.message, 'error');
    } finally {
        showLoading(false);
        fileInput.value = '';
    }
}

// Query Handler
async function sendQuery() {
    const query = queryInput.value.trim();

    if (!query) {
        showNotification('Please enter a question', 'info');
        return;
    }

    if (!isInitialized) {
        showNotification('Please upload documents first', 'warning');
        return;
    }

    // Add user message
    addMessage('You', query, 'user');
    queryInput.value = '';

    showLoading(true);

    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });

        const data = await response.json();

        if (response.ok) {
            addMessage('Assistant', data.answer, 'assistant', data.sources);
        } else {
            addMessage('System', data.error || 'Query failed', 'assistant');
        }
    } catch (error) {
        addMessage('System', 'Error: ' + error.message, 'assistant');
    } finally {
        showLoading(false);
    }
}

// UI Helpers
function addMessage(sender, content, type, sources = null) {
    clearWelcomeMessage();

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    let html = `<div class="message-content">${escapeHtml(content)}`;

    if (sources && sources.length > 0) {
        html += '<div class="sources"><div class="sources-title">📎 Sources:</div>';
        sources.forEach((source, index) => {
            html += `<div class="source-item">
                <strong>Source ${index + 1}:</strong> ${escapeHtml(source.source)}<br>
                <em>${escapeHtml(source.content)}</em>
            </div>`;
        });
        html += '</div>';
    }

    html += '</div>';

    const timestamp = new Date().toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
    });
    html += `<div class="message-meta">${escapeHtml(sender)} • ${timestamp}</div>`;

    messageDiv.innerHTML = html;
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

function clearWelcomeMessage() {
    const welcome = chatContainer.querySelector('.welcome-message');
    if (welcome) {
        welcome.remove();
    }
}

function clearChat() {
    chatContainer.innerHTML = `
        <div class="welcome-message">
            <h3>Welcome to RAG Pipeline</h3>
            <p>Upload documents to get started, then ask questions about them.</p>
            <p class="hint">The system will retrieve relevant documents and generate accurate answers.</p>
        </div>
    `;
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showLoading(show) {
    if (show) {
        loadingOverlay.classList.remove('hidden');
    } else {
        loadingOverlay.classList.add('hidden');
    }
}

function showNotification(message, type) {
    // Create a simple notification (you can enhance this with a toast library)
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        color: white;
        font-weight: 500;
        z-index: 2000;
        animation: slideIn 0.3s ease;
    `;

    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };

    notification.style.backgroundColor = colors[type] || colors.info;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Status Check
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        isInitialized = data.initialized;
        docCount.textContent = data.document_count || 0;

        if (isInitialized) {
            statusDot.classList.add('active');
            statusText.textContent = 'Ready';
            queryInput.disabled = false;
            sendBtn.disabled = false;
            systemStatus.textContent = `${data.document_count} documents indexed`;
        } else {
            statusDot.classList.remove('active');
            statusText.textContent = 'No documents';
            queryInput.disabled = true;
            sendBtn.disabled = true;
            systemStatus.textContent = 'Upload documents to get started';
        }
    } catch (error) {
        console.error('Status check error:', error);
    }
}

// Clear Index
async function clearIndex() {
    if (!confirm('Are you sure? This will delete all documents and the index.')) {
        return;
    }

    showLoading(true);

    try {
        const response = await fetch('/api/clear', {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok) {
            showNotification(data.message, 'success');
            clearChat();
            checkStatus();
        } else {
            showNotification(data.error || 'Failed to clear index', 'error');
        }
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// Utility Functions
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Add CSS animation for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
