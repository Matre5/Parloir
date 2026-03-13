// Auth check
if (!isLoggedIn()) {
    window.location.href = 'login.html';
}

document.addEventListener('DOMContentLoaded', async function() {
    console.log('Word list page loaded');
    
    // DOM elements
    const wordListContainer = document.getElementById('wordListContainer');
    const searchInput = document.getElementById('searchInput');
    const filterButtons = document.querySelectorAll('[data-filter]');
    const addWordBtn = document.getElementById('addWordBtn');
    const addWordModal = document.getElementById('addWordModal');
    const addWordForm = document.getElementById('addWordForm');
    const cancelAddBtn = document.getElementById('cancelAddBtn');
    
    // Stats elements
    const totalWords = document.getElementById('totalWords');
    const learningWords = document.getElementById('learningWords');
    const practicingWords = document.getElementById('practicingWords');
    const learnedWords = document.getElementById('learnedWords');
    
    // State
    let currentFilter = null;
    let currentSearch = null;
    let allWords = [];
    
    // Load initial data
    await loadStats();
    await loadWords();
    
    // Event listeners
    searchInput.addEventListener('input', (e) => {
        currentSearch = e.target.value.trim() || null;
        loadWords();
    });
    
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active button
            filterButtons.forEach(b => b.classList.remove('bg-primary', 'text-white'));
            filterButtons.forEach(b => b.classList.add('bg-white', 'text-primary'));
            
            btn.classList.remove('bg-white', 'text-primary');
            btn.classList.add('bg-primary', 'text-white');
            
            // Set filter
            currentFilter = btn.dataset.filter === 'all' ? null : btn.dataset.filter;
            loadWords();
        });
    });
    
    // Add word modal
    if (addWordBtn) {
        addWordBtn.addEventListener('click', () => {
            addWordModal.classList.remove('hidden');
        });
    }
    
    if (cancelAddBtn) {
        cancelAddBtn.addEventListener('click', () => {
            addWordModal.classList.add('hidden');
            addWordForm.reset();
        });
    }
    
    if (addWordForm) {
        addWordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const word = document.getElementById('newWord').value.trim();
            const translation = document.getElementById('newTranslation').value.trim();
            const context = document.getElementById('newContext').value.trim() || null;
            
            const result = await addWord(word, translation, context, 'manual');
            
            if (result.success) {
                alert('✅ Word added!');
                addWordModal.classList.add('hidden');
                addWordForm.reset();
                await loadStats();
                await loadWords();
            } else {
                alert('❌ Failed to add word: ' + result.error);
            }
        });
    }
    
    // Load statistics
    async function loadStats() {
        const result = await getWordStats();
        
        if (result.success) {
            totalWords.textContent = result.data.total;
            learningWords.textContent = result.data.learning;
            practicingWords.textContent = result.data.practicing;
            learnedWords.textContent = result.data.learned;
        }
    }
    
    // Load words
    async function loadWords() {
        wordListContainer.innerHTML = '<p class="text-center text-slate-500 py-12">Loading words...</p>';
        
        const result = await getWords(currentFilter, currentSearch);
        
        if (result.success) {
            allWords = result.data;
            displayWords(allWords);
        } else {
            wordListContainer.innerHTML = '<p class="text-center text-red-500 py-12">Failed to load words</p>';
        }
    }
    
    // Display words
    function displayWords(words) {
        if (words.length === 0) {
            wordListContainer.innerHTML = `
                <div class="text-center py-12">
                    <p class="text-slate-500 mb-4">No words found</p>
                    <button onclick="document.getElementById('addWordModal').classList.remove('hidden')" 
                            class="px-6 py-3 bg-primary text-white font-bold rounded-lg hover:bg-secondary">
                        Add Your First Word
                    </button>
                </div>
            `;
            return;
        }
        
        wordListContainer.innerHTML = words.map(word => `
            <div class="bg-white border-2 border-slate-200 rounded-lg p-6 hover:border-primary transition-colors">
                <div class="flex justify-between items-start mb-4">
                    <div class="flex-1">
                        <h3 class="text-2xl font-bold text-primary mb-1">${escapeHtml(word.word)}</h3>
                        <p class="text-lg text-slate-600 italic">${escapeHtml(word.translation)}</p>
                    </div>
                    <div class="flex gap-2">
                        <select onchange="changeStatus('${word.id}', this.value)" 
                                class="px-3 py-1 border-2 border-slate-200 rounded text-sm font-bold">
                            <option value="learning" ${word.status === 'learning' ? 'selected' : ''}>📚 Learning</option>
                            <option value="practicing" ${word.status === 'practicing' ? 'selected' : ''}>💪 Practicing</option>
                            <option value="learned" ${word.status === 'learned' ? 'selected' : ''}>✅ Learned</option>
                        </select>
                        <button onclick="deleteWordConfirm('${word.id}')" 
                                class="p-2 text-red-500 hover:bg-red-50 rounded">
                            <span class="material-symbols-outlined">delete</span>
                        </button>
                    </div>
                </div>
                
                ${word.context ? `
                    <div class="bg-slate-50 border-l-4 border-primary p-3 rounded mb-3">
                        <p class="text-sm text-slate-600"><span class="font-bold">Context:</span> "${escapeHtml(word.context)}"</p>
                    </div>
                ` : ''}
                
                <div class="flex items-center gap-4 text-xs text-slate-400">
                    <span>📍 Source: ${getSourceLabel(word.source)}</span>
                    <span>📅 Added: ${formatDate(word.created_at)}</span>
                </div>
            </div>
        `).join('');
    }
    
    // Helper functions
    window.changeStatus = async function(wordId, newStatus) {
        const result = await updateWord(wordId, newStatus);
        
        if (result.success) {
            await loadStats();
            await loadWords();
        } else {
            alert('Failed to update word status');
        }
    };
    
    window.deleteWordConfirm = async function(wordId) {
        if (confirm('Are you sure you want to delete this word?')) {
            const result = await deleteWord(wordId);
            
            if (result.success) {
                await loadStats();
                await loadWords();
            } else {
                alert('Failed to delete word');
            }
        }
    };
    
    function getSourceLabel(source) {
        const labels = {
            'chat': '💬 Chat',
            'translate': '🌍 Translator',
            'manual': '✍️ Manual'
        };
        return labels[source] || source;
    }
    
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});