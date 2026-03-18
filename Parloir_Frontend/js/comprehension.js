// Auth check
if (!isLoggedIn()) {
    window.location.href = 'login.html';
}

document.addEventListener('DOMContentLoaded', async function() {
    console.log('Comprehension page loaded');
    
    // DOM elements
    const articlesContainer = document.getElementById('articlesContainer');
    const articleView = document.getElementById('articleView');
    const articleTitle = document.getElementById('articleTitle');
    const articleContent = document.getElementById('articleContent');
    const articleImage = document.getElementById('articleImage');
    const questionsContainer = document.getElementById('questionsContainer');
    const backToArticlesBtn = document.getElementById('backToArticlesBtn');
    const startQuizBtn = document.getElementById('startQuizBtn');
    const submitAnswersBtn = document.getElementById('submitAnswersBtn');
    const resultsContainer = document.getElementById('resultsContainer');
    
    // State
    let currentArticle = null;
    let questions = [];
    let userAnswers = {};
    
    // Load articles
    await loadArticles();
    
    // Event listeners
    if (backToArticlesBtn) {
        backToArticlesBtn.addEventListener('click', () => {
            articlesContainer.classList.remove('hidden');
            articleView.classList.add('hidden');
            questionsContainer.classList.add('hidden');
            resultsContainer.classList.add('hidden');
        });
    }
    
    if (startQuizBtn) {
        startQuizBtn.addEventListener('click', async () => {
            await startQuiz();
        });
    }
    
    if (submitAnswersBtn) {
        submitAnswersBtn.addEventListener('click', () => {
            checkAllAnswers();
        });
    }
    
    // Load articles
    async function loadArticles() {
        const result = await getArticles();
        
        if (result.success) {
            displayArticles(result.data);
        } else {
            articlesContainer.innerHTML = '<p class="text-red-500 text-center py-12">Failed to load articles</p>';
        }
    }
    
    // Display articles
    function displayArticles(articles) {
        articlesContainer.innerHTML = `
            <div class="mb-8">
                <h2 class="text-3xl font-bold text-primary mb-2">Compréhension Écrite</h2>
                <p class="text-slate-600">Lisez des articles authentiques et testez votre compréhension</p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                ${articles.map(article => `
                    <div class="bg-white border-2 border-slate-200 rounded-xl overflow-hidden hover:border-primary transition-all cursor-pointer group"
                         onclick="window.selectArticle('${article.id}')">
                        <img src="${article.image_url}" alt="${escapeHtml(article.title)}" class="w-full h-48 object-cover" />
                        <div class="p-6">
                            <div class="flex items-center gap-2 mb-3">
                                <span class="px-3 py-1 bg-primary/10 text-primary text-xs font-bold rounded-full">
                                    ${article.difficulty}
                                </span>
                                <span class="text-xs text-slate-400">
                                    ${new Date(article.date).toLocaleDateString('fr-FR')}
                                </span>
                            </div>
                            <h3 class="text-lg font-bold text-slate-900 mb-2 group-hover:text-primary transition-colors">
                                ${escapeHtml(article.title)}
                            </h3>
                            <p class="text-sm text-slate-600 line-clamp-3">
                                ${escapeHtml(article.content.substring(0, 150))}...
                            </p>
                            <div class="mt-4 flex items-center gap-2 text-primary font-bold text-sm">
                                <span>Lire l'article</span>
                                <span class="group-hover:translate-x-1 transition-transform">→</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    // Select article
    window.selectArticle = async function(articleId) {
        const result = await getArticle(articleId);
        
        if (result.success) {
            currentArticle = result.data;
            displayArticle(result.data);
        } else {
            alert('Failed to load article');
        }
    };
    
    // Display article
    function displayArticle(article) {
        articleTitle.textContent = article.title;
        articleContent.innerHTML = article.content.split('\n').map(p => 
            `<p class="mb-4">${escapeHtml(p)}</p>`
        ).join('');
        
        if (article.image_url) {
            articleImage.src = article.image_url;
            articleImage.classList.remove('hidden');
        } else {
            articleImage.classList.add('hidden');
        }
        
        articlesContainer.classList.add('hidden');
        articleView.classList.remove('hidden');
        questionsContainer.classList.add('hidden');
        resultsContainer.classList.add('hidden');
    }
    
    // Start quiz
    async function startQuiz() {
        if (!currentArticle) return;
        
        // Show loading
        startQuizBtn.disabled = true;
        startQuizBtn.innerHTML = '<span class="animate-spin">⏳</span> Génération des questions...';
        
        const result = await generateQuestions(currentArticle.id);
        
        startQuizBtn.disabled = false;
        startQuizBtn.innerHTML = '📝 Commencer le Quiz';
        
        if (result.success) {
            questions = result.data;
            displayQuestions(result.data);
        } else {
            alert('Failed to generate questions: ' + result.error);
        }
    }
    
    // Display questions
    function displayQuestions(questions) {
        questionsContainer.innerHTML = `
            <div class="bg-white rounded-2xl p-8 shadow-lg">
                <h2 class="text-2xl font-bold text-primary mb-6">Questions de Compréhension</h2>
                
                <div class="space-y-8">
                    ${questions.map((q, index) => `
                        <div class="p-6 border-2 border-slate-200 rounded-xl">
                            <h3 class="font-bold text-slate-900 mb-4">
                                ${index + 1}. ${escapeHtml(q.question)}
                            </h3>
                            
                            ${q.type === 'multiple_choice' ? `
                                <div class="space-y-3">
                                    ${q.options.map((option, optIdx) => `
                                        <label class="flex items-center gap-3 cursor-pointer hover:bg-slate-50 p-3 rounded-lg transition-colors">
                                            <input type="radio" name="q${index}" value="${escapeHtml(option)}" 
                                                   class="w-5 h-5 text-primary" 
                                                   onchange="window.saveAnswer('${q.id}', this.value)">
                                            <span>${escapeHtml(option)}</span>
                                        </label>
                                    `).join('')}
                                </div>
                            ` : ''}
                            
                            ${q.type === 'true_false' ? `
                                <div class="flex gap-4">
                                    <label class="flex items-center gap-3 cursor-pointer hover:bg-slate-50 p-3 rounded-lg transition-colors flex-1">
                                        <input type="radio" name="q${index}" value="Vrai" 
                                               class="w-5 h-5 text-primary"
                                               onchange="window.saveAnswer('${q.id}', this.value)">
                                        <span>Vrai</span>
                                    </label>
                                    <label class="flex items-center gap-3 cursor-pointer hover:bg-slate-50 p-3 rounded-lg transition-colors flex-1">
                                        <input type="radio" name="q${index}" value="Faux" 
                                               class="w-5 h-5 text-primary"
                                               onchange="window.saveAnswer('${q.id}', this.value)">
                                        <span>Faux</span>
                                    </label>
                                </div>
                            ` : ''}
                            
                            ${q.type === 'short_answer' ? `
                                <textarea rows="3" 
                                          class="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-primary outline-none"
                                          placeholder="Votre réponse..."
                                          onchange="window.saveAnswer('${q.id}', this.value)"></textarea>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
                
                <div class="mt-8 flex gap-4">
                    <button onclick="document.getElementById('backToArticlesBtn').click()" 
                            class="px-6 py-3 border-2 border-slate-200 text-slate-600 font-bold rounded-lg hover:bg-slate-50">
                        Annuler
                    </button>
                    <button id="submitAnswersBtn" 
                            class="flex-1 px-6 py-3 bg-primary text-white font-bold rounded-lg hover:bg-secondary">
                        Soumettre les Réponses
                    </button>
                </div>
            </div>
        `;
        
        articleView.classList.add('hidden');
        questionsContainer.classList.remove('hidden');
        
        // Re-attach submit listener
        document.getElementById('submitAnswersBtn').addEventListener('click', () => {
            checkAllAnswers();
        });
    }
    
    // Save answer
    window.saveAnswer = function(questionId, answer) {
        userAnswers[questionId] = answer;
        console.log('Answer saved:', questionId, answer);
    };
    
    // Check all answers
    function checkAllAnswers() {
        let correctCount = 0;
        const totalQuestions = questions.length;
        
        const results = questions.map(q => {
            const userAnswer = userAnswers[q.id] || '';
            const isCorrect = userAnswer.toLowerCase().trim() === q.correct_answer.toLowerCase().trim();
            
            if (isCorrect) correctCount++;
            
            return {
                question: q.question,
                userAnswer: userAnswer,
                correctAnswer: q.correct_answer,
                isCorrect: isCorrect
            };
        });
        
        displayResults(correctCount, totalQuestions, results);
    }
    
    // Display results
    function displayResults(correctCount, totalQuestions, results) {
        const percentage = Math.round((correctCount / totalQuestions) * 100);
        
        resultsContainer.innerHTML = `
            <div class="bg-white rounded-2xl p-8 shadow-lg">
                <div class="text-center mb-8">
                    <div class="inline-block bg-primary/10 rounded-full p-8">
                        <h2 class="text-6xl font-black text-primary">${percentage}%</h2>
                        <p class="text-sm text-slate-600 font-bold uppercase mt-2">
                            ${correctCount} / ${totalQuestions} Correct
                        </p>
                    </div>
                </div>
                
                <div class="space-y-4 mb-8">
                    ${results.map((r, index) => `
                        <div class="p-6 border-2 ${r.isCorrect ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'} rounded-xl">
                            <h3 class="font-bold mb-3">${index + 1}. ${escapeHtml(r.question)}</h3>
                            <div class="space-y-2 text-sm">
                                <p><span class="font-bold">Votre réponse:</span> ${escapeHtml(r.userAnswer) || '<em>Pas de réponse</em>'}</p>
                                ${!r.isCorrect ? `
                                    <p><span class="font-bold text-green-700">Réponse correcte:</span> ${escapeHtml(r.correctAnswer)}</p>
                                ` : ''}
                                <p class="flex items-center gap-2">
                                    ${r.isCorrect ? '✅ Correct!' : '❌ Incorrect'}
                                </p>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                <div class="flex gap-4">
                    <button onclick="location.reload()" 
                            class="flex-1 px-6 py-3 bg-primary text-white font-bold rounded-lg hover:bg-secondary">
                        Nouvel Article
                    </button>
                </div>
            </div>
        `;
        
        questionsContainer.classList.add('hidden');
        resultsContainer.classList.remove('hidden');
    }
    
    // Helper function
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});