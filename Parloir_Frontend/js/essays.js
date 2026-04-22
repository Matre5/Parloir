let autoSaveInterval = null;

// Auth check
if (!isLoggedIn()) {
    window.location.href = 'login.html';
}

document.addEventListener('DOMContentLoaded', async function() {
    console.log('Essays page loaded');
    
    // DOM elements
    const promptsContainer = document.querySelector('#promptsContainer .space-y-4');
    const essayEditor = document.getElementById('essayEditor');
    const essayTextarea = document.getElementById('essayTextarea');
    const wordCountEl = document.getElementById('wordCount');
    const submitEssayBtn = document.getElementById('submitEssayBtn');
    const backToPromptsBtn = document.getElementById('backToPromptsBtn');
    const currentPromptTitle = document.getElementById('currentPromptTitle');
    const currentPromptDesc = document.getElementById('currentPromptDesc');
    const feedbackSection = document.getElementById('feedbackSection');
    const historyContainer = document.getElementById('historyContainer');
    
    // State
    let currentPromptId = null;
    let prompts = [];
    let allEssays = [];
    
    // Load prompts
    await loadPrompts();
    
    // Load history
    await loadHistory();
    
    // Event listeners
    if (essayTextarea) {
        // Load saved draft on page load (will load when prompt is selected)
        
        essayTextarea.addEventListener('input', () => {
            const count = essayTextarea.value.trim().split(/\s+/).filter(w => w.length > 0).length;
            wordCountEl.textContent = `${count} mots`;
            
            // Auto-save to localStorage
            if (currentPromptId) {
                localStorage.setItem(`essay_draft_${currentPromptId}`, essayTextarea.value);
            }
        });
    }
    
    if (submitEssayBtn) {
        submitEssayBtn.addEventListener('click', handleSubmit);
    }
    
    if (backToPromptsBtn) {
        backToPromptsBtn.addEventListener('click', () => {
            document.getElementById('promptsContainer').classList.remove('hidden');
            essayEditor.classList.add('hidden');
            feedbackSection.classList.add('hidden');
            essayTextarea.value = '';
            wordCountEl.textContent = '0 mots';
            sessionStorage.removeItem('active_prompt_id');
        });
    }
    
    // Load prompts
    async function loadPrompts() {
        console.log('Loading prompts...');
        const result = await getEssayPrompts();
        
        if (result.success) {
            prompts = result.data;
            displayPrompts(prompts);
        } else {
            promptsContainer.innerHTML = '<p class="text-red-500 text-center py-12">Failed to load prompts: ' + result.error + '</p>';
        }
    }
    
    // Display prompts
    function displayPrompts(prompts) {
        const categoryColors = {
            'personal': 'bg-secondary/10 text-secondary',
            'narrative': 'bg-accent-warm/10 text-accent-warm',
            'opinion': 'bg-primary/10 text-primary',
            'argumentative': 'bg-secondary/10 text-secondary',
            'synthesis': 'bg-accent-soft/10 text-accent-soft',
            'critical': 'bg-accent-warm/10 text-accent-warm'
        };
        
        promptsContainer.innerHTML = prompts.map(prompt => {
            const colorClass = categoryColors[prompt.category] || 'bg-slate-100 text-slate-600';
            
            return `
                <div class="group border-2 border-secondary/20 p-6 hover:border-secondary hover:bg-secondary/5 transition-all flex justify-between items-center cursor-pointer rounded-3xl"
                     onclick="window.selectPrompt('${prompt.id}')">
                    <div class="space-y-2 flex-1">
                        <span class="text-[10px] font-bold ${colorClass} px-3 py-1 rounded-full uppercase tracking-[0.2em] inline-block">
                            ${prompt.category}
                        </span>
                        <h4 class="text-lg font-bold text-slate-900 group-hover:text-primary transition-colors italic">
                            "${escapeHtml(prompt.title)}"
                        </h4>
                        <p class="text-sm text-slate-500 max-w-lg">
                            ${escapeHtml(prompt.description)}
                        </p>
                        <div class="flex gap-4 text-xs text-slate-400 mt-2">
                            <span>📝 Min ${prompt.min_words} mots</span>
                            <span>🎯 Niveau ${prompt.level}</span>
                        </div>
                    </div>
                    <div class="text-slate-300 group-hover:text-primary transition-colors text-3xl ml-4">→</div>
                </div>
            `;
        }).join('');
    }
    
    window.selectPrompt = function(promptId) {
        currentPromptId = promptId;
        sessionStorage.setItem('active_prompt_id', promptId);
        const prompt = prompts.find(p => p.id === promptId);
        
        if (!prompt) return;
        
        currentPromptTitle.textContent = prompt.title;
        currentPromptDesc.textContent = prompt.description;
        
        // Load saved draft
        const savedDraft = localStorage.getItem(`essay_draft_${promptId}`);
        if (savedDraft) {
            essayTextarea.value = savedDraft;
            const count = savedDraft.trim().split(/\s+/).filter(w => w.length > 0).length;
            wordCountEl.textContent = `${count} mots`;
        } else {
            essayTextarea.value = '';
            wordCountEl.textContent = '0 mots';
        }
        
        // Clear any existing interval
        if (autoSaveInterval) {
            clearInterval(autoSaveInterval);
        }
        
        // Auto-save every 30 seconds
        autoSaveInterval = setInterval(() => {
            if (currentPromptId && essayTextarea.value.trim()) {
                localStorage.setItem(`essay_draft_${currentPromptId}`, essayTextarea.value);
                console.log('💾 Draft auto-saved');
            }
        }, 30000); // 30 seconds
        
        document.getElementById('promptsContainer').classList.add('hidden');
        essayEditor.classList.remove('hidden');
        feedbackSection.classList.add('hidden');
        
        essayTextarea.focus();
    };
    
    // Submit essay
    async function handleSubmit() {
        const content = essayTextarea.value.trim();
        
        if (!content) {
            alert('Veuillez écrire votre essai!');
            return;
        }
        
        const wordCount = content.split(/\s+/).filter(w => w.length > 0).length;
        const prompt = prompts.find(p => p.id === currentPromptId);
        
        // Show warning if under min words
        if (wordCount < prompt.min_words) {
            const warningEl = document.createElement('div');
            warningEl.className = 'fixed top-4 right-4 bg-yellow-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
            warningEl.textContent = `⚠️ Recommandé: ${prompt.min_words} mots (vous avez ${wordCount})`;
            document.body.appendChild(warningEl);
            setTimeout(() => warningEl.remove(), 4000);
        }
        
        // Show loading
        submitEssayBtn.disabled = true;
        submitEssayBtn.innerHTML = '<span class="text-xl">⏳</span> Notation...';
        
        const result = await submitEssay(currentPromptId, content);
        
        submitEssayBtn.disabled = false;
        submitEssayBtn.innerHTML = '<span class="text-xl">→</span> Soumettre';
        
        if (result.success) {
            // Clear draft after successful submission
            sessionStorage.removeItem('active_prompt_id');
            localStorage.removeItem(`essay_draft_${currentPromptId}`);
            
            displayFeedback(result.data);
            await loadHistory();
        } else {
            alert('❌ Échec: ' + result.error);
        }
    }
    
    // Display feedback
    function displayFeedback(essay) {
        const grade = essay.grade;
        
        feedbackSection.innerHTML = `
            <div class="bg-white rounded-2xl p-8 shadow-lg">
                <div class="text-center mb-8">
                    <div class="inline-block bg-primary/10 rounded-full p-8">
                        <h2 class="text-6xl font-black text-primary">${grade.overall_score}</h2>
                        <p class="text-sm text-slate-600 font-bold uppercase">Score Global</p>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    ${createCriteriaCard('Grammaire', grade.grammar, '📝')}
                    ${createCriteriaCard('Vocabulaire', grade.vocabulary, '📚')}
                    ${createCriteriaCard('Structure', grade.structure, '🏗️')}
                    ${createCriteriaCard('Cohérence', grade.coherence, '🔗')}
                </div>
                
                <div class="mb-6 p-6 bg-green-50 border-l-4 border-green-500 rounded-lg">
                    <h3 class="font-bold text-green-800 mb-3">✨ Points Forts</h3>
                    <ul class="space-y-2">
                        ${grade.strengths.map(s => `<li class="text-green-700">✓ ${escapeHtml(s)}</li>`).join('')}
                    </ul>
                </div>
                
                <div class="p-6 bg-blue-50 border-l-4 border-blue-500 rounded-lg mb-6">
                    <h3 class="font-bold text-blue-800 mb-3">💡 Suggestions</h3>
                    <ul class="space-y-2">
                        ${grade.suggestions.map(s => `<li class="text-blue-700">→ ${escapeHtml(s)}</li>`).join('')}
                    </ul>
                </div>
                
                <!-- Show Essay Content -->
                <div class="p-6 bg-slate-50 border-2 border-slate-200 rounded-lg mb-6">
                    <h3 class="font-bold text-slate-800 mb-3">📄 Votre Essai</h3>
                    <p class="text-slate-700 whitespace-pre-wrap">${escapeHtml(essay.content)}</p>
                    <p class="text-xs text-slate-500 mt-3">${essay.word_count} mots</p>
                </div>
                
                <div class="flex gap-4">
                    <button onclick="location.reload()" 
                            class="flex-1 px-6 py-3 bg-primary text-white font-bold rounded-lg hover:bg-secondary">
                        Nouvel Essai
                    </button>
                </div>
            </div>
        `;
        
        essayEditor.classList.add('hidden');
        feedbackSection.classList.remove('hidden');
    }
    
    // Create criteria card
    function createCriteriaCard(title, criteria, icon) {
        const scoreColor = criteria.score >= 80 ? 'text-green-600' : 
                          criteria.score >= 60 ? 'text-yellow-600' : 'text-red-600';
        
        return `
            <div class="p-6 border-2 border-slate-200 rounded-xl hover:border-primary transition-colors">
                <div class="flex justify-between items-center mb-3">
                    <h3 class="font-bold text-slate-900">${icon} ${title}</h3>
                    <span class="text-2xl font-black ${scoreColor}">${criteria.score}</span>
                </div>
                <p class="text-sm text-slate-600 mb-3">${escapeHtml(criteria.feedback)}</p>
                ${criteria.examples && criteria.examples.length > 0 ? `
                    <div class="text-xs text-slate-500 space-y-1">
                        ${criteria.examples.map(ex => `<p class="italic">• ${escapeHtml(ex)}</p>`).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    // Load history
    async function loadHistory() {
        const result = await getEssayHistory();
        
        if (result.success && result.data.length > 0) {
            allEssays = result.data;
            
            historyContainer.innerHTML = `
                <h2 class="text-2xl font-bold text-primary mb-6">📚 Mes Essais Précédents</h2>
                <div class="space-y-4">
                    ${result.data.map((essay, index) => `
                        <div class="bg-white border-2 border-slate-200 rounded-lg p-6 hover:border-primary transition-colors cursor-pointer"
                             onclick="window.viewEssayDetails(${index})">
                            <div class="flex justify-between items-start mb-3">
                                <div>
                                    <h3 class="font-bold text-lg text-slate-900">${escapeHtml(essay.prompt_title)}</h3>
                                    <p class="text-sm text-slate-500">
                                        ${new Date(essay.submitted_at).toLocaleDateString('fr-FR', {
                                            day: 'numeric',
                                            month: 'long',
                                            year: 'numeric'
                                        })}
                                    </p>
                                </div>
                                <div class="text-right">
                                    <div class="text-3xl font-black text-primary">${essay.grade.overall_score}</div>
                                    <p class="text-xs text-slate-500">${essay.word_count} mots</p>
                                </div>
                            </div>
                            <div class="flex gap-2 flex-wrap">
                                <span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full">
                                    📝 ${essay.grade.grammar.score}
                                </span>
                                <span class="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded-full">
                                    📚 ${essay.grade.vocabulary.score}
                                </span>
                                <span class="px-3 py-1 bg-purple-100 text-purple-700 text-xs font-bold rounded-full">
                                    🏗️ ${essay.grade.structure.score}
                                </span>
                                <span class="px-3 py-1 bg-orange-100 text-orange-700 text-xs font-bold rounded-full">
                                    🔗 ${essay.grade.coherence.score}
                                </span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            historyContainer.innerHTML = '';
        }
    }

    const savedPromptId = sessionStorage.getItem('active_prompt_id');
    if (savedPromptId && prompts.find(p => p.id === savedPromptId)) {
        window.selectPrompt(savedPromptId);
    }
    
    // View essay details
    window.viewEssayDetails = function(index) {
        const essay = allEssays[index];
        
        if (!essay) return;
        
        // Hide prompts and editor
        document.getElementById('promptsContainer').classList.add('hidden');
        essayEditor.classList.add('hidden');
        
        // Display the full feedback
        displayFeedback(essay);
        
        // Scroll to feedback
        feedbackSection.scrollIntoView({ behavior: 'smooth' });
    };
    
    // Helper function
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});