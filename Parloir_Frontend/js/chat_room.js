// Auth check
if (!isLoggedIn()) {
    window.location.href = 'login.html';
}

// User is logged in - get their info
const user = getCurrentUser();
const userName = getUserName();

console.log("Logged in as:", user);
console.log("User name:", userName);

document.addEventListener("DOMContentLoaded", function () {
// Try multiple sources for the name
const storedName = localStorage.getItem("user_name");
const user = getCurrentUser();
const userEmail = user?.email || "";
const emailName = userEmail.split("@")[0];

// Use stored name first, then email username, then 'User'
const displayName = storedName || emailName || "User";

const welcomeEl = document.getElementById("welcomeMessage");
if (welcomeEl) {
    welcomeEl.textContent = `Welcome, ${displayName}!`;
}

console.log("Display name:", displayName);
console.log("Stored name:", storedName);
console.log("User:", user);
});

// Get DOM elements
const chatContainer = document.querySelector('.flex-1.space-y-8');
const messageInput = document.querySelector('input[type="text"]');
// const sendButton = document.querySelector('button .material-symbols-outlined:last-child').parentElement;
const sendButton = document.querySelector('button .material-symbols-outlined[textContent="send"]')?.parentElement || 
                   Array.from(document.querySelectorAll('button')).find(btn => 
                       btn.querySelector('.material-symbols-outlined')?.textContent?.includes('send')
                   );
const suggestionButtons = document.querySelectorAll('.px-4.py-2.bg-white');

// Conversation history
let conversationHistory = JSON.parse(localStorage.getItem("chat_history")) || [];

// Clear initial demo messages
chatContainer.innerHTML = '';

// Send message function
async function sendMessage(messageText) {
    if (!messageText.trim()) return;

    // Add user message to UI
    addUserMessage(messageText);

    // Clear input
    messageInput.value = '';

    // Show typing indicator
    const typingId = showTypingIndicator();

    try {
        // Call API
        const response = await authFetch('http://localhost:8001/api/chat/chat', {
            method: 'POST',
            body: JSON.stringify({
                message: messageText,
                conversation_history: conversationHistory
            })
        });

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator(typingId);

        if (response.ok) {
            // Add AI response to UI
            addAIMessage(data.response);

            // Update conversation history
            conversationHistory.push(
                { role: 'user', content: messageText },
                { role: 'assistant', content: data.response }
            );

            localStorage.setItem("chat_history", JSON.stringify(conversationHistory));
        } else {
            throw new Error(data.detail || 'Failed to get response');
        }

    } catch (error) {
        console.error('Chat error:', error);
        removeTypingIndicator(typingId);
        addAIMessage("Désolé, j'ai rencontré un problème. Pouvez-vous réessayer ?");
    }
}

// Add user message to UI
function addUserMessage(text) {
    const userName = getUserName() || 'Vous';
    
    const messageHTML = `
        <div class="flex items-end gap-3 max-w-[85%] ml-auto flex-row-reverse">
            <div class="size-10 rounded-full bg-primary flex items-center justify-center shrink-0 shadow-lg shadow-primary/20 overflow-hidden">
                <span class="material-symbols-outlined text-white">person</span>
            </div>
            <div class="flex flex-col gap-1.5 items-end">
                <span class="text-[11px] font-bold text-primary uppercase mr-2">${userName}</span>
                <div class="chat-bubble-user bg-primary text-white p-4 rounded-2xl shadow-md">
                    <p class="text-lg leading-relaxed">${escapeHtml(text)}</p>
                </div>
            </div>
        </div>
    `;
    
    chatContainer.insertAdjacentHTML('beforeend', messageHTML);
    scrollToBottom();
}

// Add AI message to UI
function addAIMessage(text) {
    const messageHTML = `
        <div class="flex items-end gap-3 max-w-[85%]">
            <div class="size-10 rounded-full bg-accent-light/20 flex items-center justify-center shrink-0 border-2 border-accent-light/30">
                <span class="material-symbols-outlined text-accent-dark">smart_toy</span>
            </div>
            <div class="flex flex-col gap-1.5">
                <span class="text-[11px] font-bold text-accent-dark uppercase ml-2">Tuteur IA</span>
                <div class="chat-bubble-ai bg-white dark:bg-slate-800 p-4 rounded-2xl shadow-sm border border-primary/5">
                    <p class="text-lg leading-relaxed">${escapeHtml(text)}</p>
                    <div class="mt-3 pt-3 border-t border-slate-100 dark:border-slate-700 flex gap-4">
                        <button class="flex items-center gap-1.5 text-xs font-semibold text-secondary hover:text-primary transition-colors">
                            <span class="material-symbols-outlined text-sm">volume_up</span>
                            Écouter
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    chatContainer.insertAdjacentHTML('beforeend', messageHTML);
    scrollToBottom();
}

// Show typing indicator
function showTypingIndicator() {
    const id = 'typing-' + Date.now();
    const typingHTML = `
        <div class="flex items-end gap-3 max-w-[85%]" id="${id}">
            <div class="size-10 rounded-full bg-accent-light/20 flex items-center justify-center shrink-0 border-2 border-accent-light/30">
                <span class="material-symbols-outlined text-accent-dark">smart_toy</span>
            </div>
            <div class="flex flex-col gap-1.5">
                <span class="text-[11px] font-bold text-accent-dark uppercase ml-2">Tuteur IA</span>
                <div class="chat-bubble-ai bg-white dark:bg-slate-800 p-4 rounded-2xl shadow-sm border border-primary/5">
                    <div class="flex gap-1">
                        <div class="w-2 h-2 bg-accent-light rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                        <div class="w-2 h-2 bg-accent-light rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                        <div class="w-2 h-2 bg-accent-light rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                    </div>
                </div>
            </div>
        </div>
    `;
    chatContainer.insertAdjacentHTML('beforeend', typingHTML);
    scrollToBottom();
    return id;
}

// Remove typing indicator
function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) element.remove();
}

// Scroll to bottom
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Event listeners
sendButton.addEventListener('click', () => {
    sendMessage(messageInput.value);
});

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage(messageInput.value);
    }
});

// Suggestion buttons
suggestionButtons.forEach(button => {
    button.addEventListener('click', () => {
        const text = button.textContent.trim().replace(/['"]/g, '');
        messageInput.value = text;
        sendMessage(text);
    });
});

// Initial greeting
addAIMessage("Bonjour ! Je suis votre tuteur de français. Comment puis-je vous aider aujourd'hui ? 😊");