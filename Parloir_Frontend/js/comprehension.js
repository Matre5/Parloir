// Auth check
if (!isLoggedIn()) {
    window.location.href = 'login.html';
}

document.addEventListener('DOMContentLoaded', async function() {
    console.log('Comprehension page loaded');
    
    // DOM elements
    const articleTitle = document.getElementById('articleTitle');
    const articleContent = document.getElementById('articleContent');
    const startQuizBtn = document.getElementById('startQuizBtn');
    const questionsContainer = document.getElementById('questionsContainer');
    const articleView = document.getElementById('articleView');
    const resultsContainer = document.getElementById('resultsContainer');
    
    // State
    let questions = [];
    let userAnswers = {};
    
    // Load today's article
    await loadTodaysArticle();
    
    // Event listeners
    if (startQuizBtn) {
        startQuizBtn.addEventListener('click', startQuiz);
    }
    
    // Load today's article
    async function loadTodaysArticle() {
        const result = await getTodaysArticle();
        
        if (result.success) {
            displayArticle(result.data);
        } else {
            alert('Failed to load article: ' + result.error);
        }
    }
    
    // Display article
    function displayArticle(article) {
        if (articleTitle) {
            articleTitle.textContent = article.title;
        }
        
        if (articleContent) {
            // Split content into paragraphs
            const paragraphs = article.content.split('\n\n').filter(p => p.trim());
            articleContent.innerHTML = paragraphs.map(p => 
                `<p class="text-[#0e141b] text-base font-normal leading-normal mb-4">${escapeHtml(p)}</p>`
            ).join('');
        }
    }
    
    // Start quiz
    async function startQuiz() {
        startQuizBtn.disabled = true;
        startQuizBtn.querySelector('.truncate').textContent = '⏳ Génération des questions...';
        
        const result = await generateComprehensionQuestions();
        
        startQuizBtn.disabled = false;
        startQuizBtn.querySelector('.truncate').textContent = '📝 QUIZ DE COMPRÉHENSION';
        
        if (result.success) {
            questions = result.data;
            displayQuestions(result.data);
        } else {
            alert('Failed to generate questions: ' + result.error);
        }
    }
    
    // Display questions
    function displayQuestions(questions) {
        const questionsHTML = questions.map((q, index) => {
            if (q.type === 'multiple_choice') {
                return `
                    <div class="flex flex-col gap-2">
                        <p class="text-white text-base font-bold leading-normal">
                            ${index + 1}. ${escapeHtml(q.question)}
                        </p>
                        <div class="grid grid-cols-2 gap-3">
                            ${q.options.map((option, optIdx) => `
                                <label class="flex items-center gap-3 cursor-pointer bg-white/10 hover:bg-white/20 p-3 rounded-lg transition-colors">
                                    <input type="radio" name="q${index}" value="${escapeHtml(option)}" 
                                           class="w-5 h-5"
                                           onchange="window.saveAnswer('${q.id}', this.value)">
                                    <span class="text-white">${String.fromCharCode(65 + optIdx)}) ${escapeHtml(option)}</span>
                                </label>
                            `).join('')}
                        </div>
                    </div>
                `;
            } else if (q.type === 'true_false') {
                return `
                    <div class="flex flex-col gap-2">
                        <p class="text-white text-base font-bold leading-normal">
                            ${index + 1}. ${escapeHtml(q.question)}
                        </p>
                        <div class="grid grid-cols-2 gap-3">
                            <label class="flex items-center gap-3 cursor-pointer bg-white/10 hover:bg-white/20 p-3 rounded-lg transition-colors">
                                <input type="radio" name="q${index}" value="Vrai" 
                                       class="w-5 h-5"
                                       onchange="window.saveAnswer('${q.id}', this.value)">
                                <span class="text-white">A) Vrai</span>
                            </label>
                            <label class="flex items-center gap-3 cursor-pointer bg-white/10 hover:bg-white/20 p-3 rounded-lg transition-colors">
                                <input type="radio" name="q${index}" value="Faux" 
                                       class="w-5 h-5"
                                       onchange="window.saveAnswer('${q.id}', this.value)">
                                <span class="text-white">B) Faux</span>
                            </label>
                        </div>
                    </div>
                `;
            }
        }).join('');
        
        questionsContainer.innerHTML = `
            <div class="flex flex-col gap-2 rounded-xl bg-[#019863] p-6">
                <h2 class="text-white text-[22px] font-bold leading-tight tracking-[-0.015em]">
                    📝 QUIZ DE COMPRÉHENSION
                </h2>
                <div class="flex flex-col gap-6 mt-4">
                    ${questionsHTML}
                </div>
                <div class="flex justify-center mt-6">
                    <button id="submitAnswersBtn" class="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-xl h-12 px-5 bg-[#e673ac] text-[#110a03] text-base font-bold leading-normal grow">
                        <span class="truncate">VÉRIFIER MES RÉPONSES</span>
                    </button>
                </div>
            </div>
        `;
        
        // Hide article, show questions
        if (articleView) articleView.classList.add('hidden');
        questionsContainer.classList.remove('hidden');
        
        // Attach submit listener
        document.getElementById('submitAnswersBtn').addEventListener('click', checkAllAnswers);
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
            <div class="flex flex-col gap-6 px-4 py-10">
                <div class="bg-white rounded-2xl p-8 shadow-lg">
                    <div class="text-center mb-8">
                        <div class="inline-block bg-[#019863]/10 rounded-full p-8">
                            <h2 class="text-6xl font-black text-[#019863]">${percentage}%</h2>
                            <p class="text-sm text-slate-600 font-bold uppercase mt-2">
                                ${correctCount} / ${totalQuestions} Correct
                            </p>
                        </div>
                    </div>
                    
                    <div class="space-y-4 mb-8">
                        ${results.map((r, index) => `
                            <div class="p-6 border-2 ${r.isCorrect ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'} rounded-xl">
                                <h3 class="font-bold mb-3 text-[#0e141b]">${index + 1}. ${escapeHtml(r.question)}</h3>
                                <div class="space-y-2 text-sm">
                                    <p class="text-[#0e141b]"><span class="font-bold">Votre réponse:</span> ${escapeHtml(r.userAnswer) || '<em>Pas de réponse</em>'}</p>
                                    ${!r.isCorrect ? `
                                        <p class="text-[#0e141b]"><span class="font-bold text-green-700">Réponse correcte:</span> ${escapeHtml(r.correctAnswer)}</p>
                                    ` : ''}
                                    <p class="flex items-center gap-2">
                                        ${r.isCorrect ? '✅ Correct!' : '❌ Incorrect'}
                                    </p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="flex justify-center">
                        <button onclick="location.reload()" class="px-8 py-4 bg-[#019863] text-white font-bold rounded-lg hover:bg-[#019863]/90">
                            Revenir à l'article
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        questionsContainer.classList.add('hidden');
        resultsContainer.classList.remove('hidden');
    }
    
    // Helper
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});