// CONFIG
const API_BASE_URL = 'http://localhost:8001/api';

function getToken() {
    return localStorage.getItem('access_token');
}

// AUTH CHECK
if (!isLoggedIn()) {
    window.location.href = 'login.html';
}

// STATE
const state = {
    article: null,
    questions: [],
    answers: {}
};

// DOM ELEMENTS
const elements = {
    articleTitle: document.getElementById('articleTitle'),
    articleContent: document.getElementById('articleContent'),
    startQuizBtn: document.getElementById('startQuizBtn'),
    questionsContainer: document.getElementById('questionsContainer'),
    articleView: document.getElementById('articleView'),
    resultsContainer: document.getElementById('resultsContainer'),
    levelDesc: document.getElementById('levelDesc'),
    userLevel: document.getElementById('userLevel')
};

// INIT
document.addEventListener('DOMContentLoaded', init);

async function init() {
    console.log('Comprehension page loaded');
    await loadArticle();
    elements.startQuizBtn?.addEventListener('click', handleStartQuiz);
}

// API LAYER
async function apiCall(endpoint, method = 'GET') {
    const token = getToken();

    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    });

    const data = await res.json();

    if (!res.ok) {
        throw new Error(data.detail || 'API Error');
    }

    return data;
}

// LOAD ARTICLE
async function loadArticle() {
    try {
        console.log('Loading article...');
        const article = await apiCall('/comprehension/today');
        console.log('Article loaded:', article);
        
        state.article = article;
        renderArticle(article);
    } catch (err) {
        console.error('Load article error:', err);
        elements.articleContent.innerHTML = `
            <div class="text-center py-12">
                <p class="text-red-500 font-bold mb-4">❌ Échec du chargement</p>
                <p class="text-slate-600 mb-4">${err.message}</p>
                <button onclick="location.reload()" class="px-6 py-2 bg-primary text-white rounded-lg">
                    Réessayer
                </button>
            </div>
        `;
    }
}

function renderArticle(article) {
    // Update title
    elements.articleTitle.textContent = article.title;
    
    // Update level badges
    const levelMap = {
        'A1': 'Débutant',
        'A2': 'Élémentaire', 
        'B1': 'Intermédiaire',
        'B2': 'Intermédiaire Avancé',
        'C1': 'Avancé',
        'C2': 'Maîtrise'
    };
    
    if (elements.levelDesc) {
        elements.levelDesc.textContent = `Niveau ${levelMap[article.difficulty] || article.difficulty}`;
    }
    
    if (elements.userLevel) {
        elements.userLevel.textContent = `Français (${article.difficulty})`;
    }

    // Split content into paragraphs
    const paragraphs = article.content.split('\n\n').filter(p => p.trim());

    elements.articleContent.innerHTML = paragraphs
        .map(p => `<p class="text-slate-700 text-lg leading-relaxed mb-6">${makeWordsClickable(p.trim())}</p>`)
        .join('');
    
    // UPDATE CULTURAL CONTEXT IN SIDEBAR
    updateCulturalContext(article.cultural_context || []);
}

// UPDATE CULTURAL CONTEXT SIDEBAR
function updateCulturalContext(contexts) {
    // Find the cultural context container by ID
    const contextContainer = document.getElementById('culturalContextContainer');
    
    if (!contextContainer) {
        console.error('Cultural context container not found');
        return;
    }
    
    if (!contexts || contexts.length === 0) {
        console.log('No cultural context provided');
        contextContainer.innerHTML = `
            <h4 class="text-xs font-black text-slate-400 uppercase tracking-widest">Contexte Culturel</h4>
            <div class="space-y-4">
                <p class="text-xs text-slate-500 italic">Pas de contexte disponible</p>
            </div>
        `;
        return;
    }
    
    console.log('Updating cultural context with', contexts.length, 'items:', contexts);
    
    // Build cultural context HTML
    const contextHTML = contexts.map(ctx => `
        <div class="flex gap-3">
            <span class="material-symbols-outlined text-accent-green">${ctx.icon}</span>
            <div>
                <p class="text-xs font-bold text-slate-700 mb-1">${escapeHtml(ctx.title)}</p>
                <p class="text-xs text-slate-600">${escapeHtml(ctx.text)}</p>
            </div>
        </div>
    `).join('');
    
    // Update the container
    contextContainer.innerHTML = `
        <h4 class="text-xs font-black text-slate-400 uppercase tracking-widest">Contexte Culturel</h4>
        <div class="space-y-4">
            ${contextHTML}
        </div>
    `;
}

// START QUIZ
async function handleStartQuiz() {
    setLoading(true);

    try {
        console.log('Generating questions...');
        const questions = await apiCall('/comprehension/questions', 'POST');
        console.log('Questions generated:', questions);
        
        state.questions = questions;
        renderQuestions(questions);
    } catch (err) {
        console.error('Generate questions error:', err);
        alert('❌ Échec de génération des questions: ' + err.message);
    } finally {
        setLoading(false);
    }
}

function setLoading(isLoading) {
    elements.startQuizBtn.disabled = isLoading;
    
    if (isLoading) {
        elements.startQuizBtn.innerHTML = `
            <span class="material-symbols-outlined animate-spin">progress_activity</span>
            <span>Génération...</span>
        `;
    } else {
        elements.startQuizBtn.innerHTML = `
            <span class="material-symbols-outlined">quiz</span>
            <span>Quiz de Compréhension</span>
        `;
    }
}

// RENDER QUESTIONS
function renderQuestions(questions) {
    const html = questions.map((q, i) => renderQuestion(q, i)).join('');

    elements.questionsContainer.innerHTML = `
        <div class="bg-accent-green rounded-2xl p-8 shadow-lg">
            <div class="flex items-center gap-3 mb-8">
                <span class="material-symbols-outlined text-white text-3xl">quiz</span>
                <h2 class="text-white text-3xl font-black">Quiz de Compréhension</h2>
            </div>

            <div class="flex flex-col gap-8">
                ${html}
            </div>

            <div class="flex justify-center mt-8 pt-8 border-t-2 border-white/20">
                <button id="submitBtn" class="px-10 py-4 bg-accent-pink text-white rounded-xl font-black text-sm uppercase tracking-wider hover:bg-accent-burgundy transition-colors shadow-lg">
                    Vérifier mes réponses
                </button>
            </div>
        </div>
    `;

    elements.articleView.classList.add('hidden');
    elements.questionsContainer.classList.remove('hidden');

    document.getElementById('submitBtn')
        .addEventListener('click', checkAnswers);
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function renderQuestion(q, index) {
    if (q.type === 'multiple_choice') {
        return `
        <div class="bg-white/5 p-6 rounded-xl">
            <p class="text-white text-lg font-bold mb-4">${index + 1}. ${escapeHtml(q.question)}</p>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                ${q.options.map((opt, i) => `
                    <label class="flex items-start gap-3 bg-white/10 hover:bg-white/20 p-4 rounded-xl cursor-pointer transition-all border-2 border-transparent hover:border-white/30">
                        <input type="radio" name="${q.id}" value="${escapeHtml(opt)}" class="mt-1 w-5 h-5"
                            onchange="handleAnswer('${q.id}', this.value)">
                        <span class="text-white flex-1">
                            <strong>${String.fromCharCode(65 + i)})</strong> ${escapeHtml(opt)}
                        </span>
                    </label>
                `).join('')}
            </div>
        </div>
        `;
    }

    if (q.type === 'true_false') {
        return `
        <div class="bg-white/5 p-6 rounded-xl">
            <p class="text-white text-lg font-bold mb-4">${index + 1}. ${escapeHtml(q.question)}</p>
            <div class="grid grid-cols-2 gap-3">
                ${['Vrai', 'Faux'].map((val, i) => `
                    <label class="flex items-center gap-3 bg-white/10 hover:bg-white/20 p-4 rounded-xl cursor-pointer transition-all border-2 border-transparent hover:border-white/30">
                        <input type="radio" name="${q.id}" value="${val}" class="w-5 h-5"
                            onchange="handleAnswer('${q.id}', this.value)">
                        <span class="text-white font-bold">${String.fromCharCode(65 + i)}) ${val}</span>
                    </label>
                `).join('')}
            </div>
        </div>
        `;
    }

    return '';
}

// ANSWERS
window.handleAnswer = function (questionId, value) {
    state.answers[questionId] = value;
    console.log('Answer saved:', questionId, '=', value);
};

// CHECK ANSWERS
function checkAnswers() {
    // Notify backend — updates streak + usage count
    authFetch(`${API_BASE_URL}/comprehension/submit-quiz`, { method: 'POST' }).catch(() => {});

    console.log('Checking answers:', state.answers);
    
    let correct = 0;

    const results = state.questions.map(q => {
        const user = (state.answers[q.id] || '').trim().toLowerCase();
        const correctAns = (q.correct_answer || '').trim().toLowerCase();

        const isCorrect = user === correctAns;

        if (isCorrect) correct++;

        return {
            question: q.question,
            userAnswer: state.answers[q.id] || '',
            correctAnswer: q.correct_answer,
            isCorrect
        };
    });

    console.log('Results:', correct, '/', state.questions.length);
    renderResults(correct, state.questions.length, results);
}

// RESULTS
function renderResults(correct, total, results) {
    const percent = Math.round((correct / total) * 100);

    elements.resultsContainer.innerHTML = `
        <div class="bg-white rounded-2xl p-8 shadow-lg border-2 border-slate-100">
            <div class="text-center mb-10">
                <div class="inline-block bg-accent-green/10 rounded-full p-10">
                    <h2 class="text-7xl font-black text-accent-green">${percent}%</h2>
                    <p class="text-slate-600 font-bold uppercase mt-3 text-sm tracking-wider">
                        ${correct} / ${total} Correct${correct > 1 ? 's' : ''}
                    </p>
                </div>
            </div>

            <div class="space-y-4 mb-10">
                ${results.map((r, i) => `
                    <div class="p-6 rounded-xl border-2 ${r.isCorrect ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}">
                        <p class="font-bold text-slate-900 text-lg mb-3">${i + 1}. ${escapeHtml(r.question)}</p>
                        <div class="space-y-2">
                            <p class="text-slate-700">
                                <span class="font-bold">Votre réponse:</span> 
                                ${r.userAnswer ? escapeHtml(r.userAnswer) : '<em class="text-slate-400">Pas de réponse</em>'}
                            </p>
                            ${!r.isCorrect ? `
                                <p class="text-slate-700">
                                    <span class="font-bold text-green-700">Réponse correcte:</span> 
                                    ${escapeHtml(r.correctAnswer)}
                                </p>
                            ` : ''}
                            <p class="text-lg font-bold ${r.isCorrect ? 'text-green-600' : 'text-red-600'}">
                                ${r.isCorrect ? '✅ Correct!' : '❌ Incorrect'}
                            </p>
                        </div>
                    </div>
                `).join('')}
            </div>

            <div class="flex justify-center">
                <button onclick="location.reload()" class="px-8 py-4 bg-accent-green text-white rounded-xl font-black text-sm uppercase tracking-wider hover:bg-primary transition-colors shadow-lg">
                    Nouvel Article Demain
                </button>
            </div>
        </div>
    `;

    elements.questionsContainer.classList.add('hidden');
    elements.resultsContainer.classList.remove('hidden');
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// HELPERS
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function makeWordsClickable(text) {
    return text.replace(/([a-zA-ZÀ-ÿ'-]+)/g, (word) => {
        return `<span class="cursor-pointer hover:bg-primary/10 hover:text-primary rounded px-0.5 transition-colors word-clickable" onclick="translateWord('${word}')">${word}</span>`;
    });
}

window.translateWord = function(word) {
    window.location.href = `translate.html?word=${encodeURIComponent(word)}`;
};