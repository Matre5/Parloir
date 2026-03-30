// ============================================
// AUTH CHECK
// ============================================
if (!isLoggedIn()) {
    window.location.href = 'login.html';
}

// ============================================
// STATE
// ============================================
const state = {
    article: null,
    questions: [],
    answers: {}
};

// ============================================
// DOM ELEMENTS
// ============================================
const elements = {
    articleTitle: document.getElementById('articleTitle'),
    articleContent: document.getElementById('articleContent'),
    startQuizBtn: document.getElementById('startQuizBtn'),
    questionsContainer: document.getElementById('questionsContainer'),
    articleView: document.getElementById('articleView'),
    resultsContainer: document.getElementById('resultsContainer')
};

// ============================================
// INIT
// ============================================
document.addEventListener('DOMContentLoaded', init);

async function init() {
    console.log('Comprehension page loaded');

    await loadArticle();

    elements.startQuizBtn?.addEventListener('click', handleStartQuiz);
}

// ============================================
// API LAYER (IMPORTANT FOR SCALE)
// ============================================
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

// ============================================
// LOAD ARTICLE
// ============================================
async function loadArticle() {
    try {
        const article = await apiCall('/comprehension/today');
        state.article = article;
        renderArticle(article);
    } catch (err) {
        alert('Failed to load article: ' + err.message);
    }
}

function renderArticle(article) {
    elements.articleTitle.textContent = article.title;

    const paragraphs = article.content.split('\n\n');

    elements.articleContent.innerHTML = paragraphs
        .map(p => `<p class="text-[#0e141b] text-base leading-normal mb-4">${escapeHtml(p)}</p>`)
        .join('');
}

// ============================================
// START QUIZ
// ============================================
async function handleStartQuiz() {
    setLoading(true);

    try {
        const questions = await apiCall('/comprehension/questions', 'POST');

        state.questions = questions;
        renderQuestions(questions);

    } catch (err) {
        alert('Failed to generate questions: ' + err.message);
    } finally {
        setLoading(false);
    }
}

function setLoading(isLoading) {
    elements.startQuizBtn.disabled = isLoading;

    const label = elements.startQuizBtn.querySelector('.truncate');
    if (label) {
        label.textContent = isLoading
            ? '⏳ Génération...'
            : '📝 QUIZ DE COMPRÉHENSION';
    }
}

// ============================================
// RENDER QUESTIONS
// ============================================
function renderQuestions(questions) {
    const html = questions.map((q, i) => renderQuestion(q, i)).join('');

    elements.questionsContainer.innerHTML = `
        <div class="flex flex-col gap-2 rounded-xl bg-[#019863] p-6">
            <h2 class="text-white text-[22px] font-bold">
                📝 QUIZ DE COMPRÉHENSION
            </h2>

            <div class="flex flex-col gap-6 mt-4">
                ${html}
            </div>

            <div class="flex justify-center mt-6">
                <button id="submitBtn" class="px-6 py-3 bg-[#e673ac] rounded-xl font-bold">
                    Vérifier
                </button>
            </div>
        </div>
    `;

    elements.articleView.classList.add('hidden');
    elements.questionsContainer.classList.remove('hidden');

    document.getElementById('submitBtn')
        .addEventListener('click', checkAnswers);
}

function renderQuestion(q, index) {
    if (q.type === 'multiple_choice') {
        return `
        <div>
            <p class="text-white font-bold mb-2">${index + 1}. ${escapeHtml(q.question)}</p>
            <div class="grid grid-cols-2 gap-3">
                ${q.options.map((opt, i) => `
                    <label class="bg-white/10 p-3 rounded-lg cursor-pointer">
                        <input type="radio" name="${q.id}" value="${escapeHtml(opt)}"
                            onchange="handleAnswer('${q.id}', this.value)">
                        <span class="text-white">${String.fromCharCode(65 + i)}) ${escapeHtml(opt)}</span>
                    </label>
                `).join('')}
            </div>
        </div>
        `;
    }

    if (q.type === 'true_false') {
        return `
        <div>
            <p class="text-white font-bold mb-2">${index + 1}. ${escapeHtml(q.question)}</p>
            <div class="grid grid-cols-2 gap-3">
                ${['Vrai', 'Faux'].map(val => `
                    <label class="bg-white/10 p-3 rounded-lg cursor-pointer">
                        <input type="radio" name="${q.id}" value="${val}"
                            onchange="handleAnswer('${q.id}', this.value)">
                        <span class="text-white">${val}</span>
                    </label>
                `).join('')}
            </div>
        </div>
        `;
    }

    return '';
}

// ============================================
// ANSWERS
// ============================================
window.handleAnswer = function (questionId, value) {
    state.answers[questionId] = value;
};

// ============================================
// CHECK ANSWERS
// ============================================
function checkAnswers() {
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

    renderResults(correct, state.questions.length, results);
}

// ============================================
// RESULTS
// ============================================
function renderResults(correct, total, results) {
    const percent = Math.round((correct / total) * 100);

    elements.resultsContainer.innerHTML = `
        <div class="p-6 bg-white rounded-xl shadow">
            <div class="text-center mb-6">
                <h2 class="text-5xl font-bold text-[#019863]">${percent}%</h2>
                <p>${correct} / ${total}</p>
            </div>

            ${results.map((r, i) => `
                <div class="p-4 mb-3 rounded-lg border ${r.isCorrect ? 'bg-green-50' : 'bg-red-50'}">
                    <p class="font-bold">${i + 1}. ${escapeHtml(r.question)}</p>
                    <p><b>Votre réponse:</b> ${escapeHtml(r.userAnswer || '—')}</p>
                    ${!r.isCorrect ? `<p><b>Correct:</b> ${escapeHtml(r.correctAnswer)}</p>` : ''}
                </div>
            `).join('')}

            <button onclick="location.reload()" class="mt-4 px-6 py-3 bg-[#019863] text-white rounded-lg">
                Recommencer
            </button>
        </div>
    `;

    elements.questionsContainer.classList.add('hidden');
    elements.resultsContainer.classList.remove('hidden');
}

// ============================================
// HELPERS
// ============================================
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}