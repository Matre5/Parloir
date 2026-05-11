// Auth check
if (!isLoggedIn()) {
    window.location.href = 'login.html';
}

document.addEventListener('DOMContentLoaded', function() {

    // DOM elements
    const searchInput = document.querySelector('input[type="text"]');
    const wordDisplay = document.getElementById('wordDisplay');
    const phoneticDisplay = document.getElementById('phoneticDisplay');
    const audioBtn = document.querySelector('button:has(.material-symbols-outlined)');
    const allBtns = document.querySelectorAll('button');
    
    let audioBtn_ = null;
    let recordBtn = null;
    allBtns.forEach(btn => {
        const icon = btn.querySelector('.material-symbols-outlined');
        if (!icon) return;
        if (icon.textContent.trim() === 'volume_up') audioBtn_ = btn;
        if (icon.textContent.trim() === 'mic') recordBtn = btn;
    });

    // State
    let currentWord = 'parler';
    let wordsRecorded = parseInt(sessionStorage.getItem('words_recorded') || '0');
    
    // Phonetic guide map (expand as needed)
    const phoneticMap = {
        'parler': '/pah-lay/', 'bonjour': '/bon-zhoor/', 'merci': '/mair-see/',
        'oui': '/wee/', 'non': '/noh/', 'bonsoir': '/bon-swahr/',
        'au revoir': '/oh ruh-vwahr/', 'comment': '/koh-mahn/',
        'français': '/frahn-say/', 'manger': '/mahn-zhay/',
        'habiter': '/ah-bee-tay/', 'vouloir': '/voo-lwahr/',
        'pouvoir': '/poo-vwahr/', 'savoir': '/sah-vwahr/',
        'être': '/eh-truh/', 'avoir': '/ah-vwahr/',
        'faire': '/fair/', 'aller': '/ah-lay/',
        'venir': '/vuh-neer/', 'prendre': '/prahn-druh/',
        'salut': '/sah-loo/', 'bonne nuit': '/bon nwee/', 'excusez-moi': '/ex-kyoo-zay mwah/',
        'je': '/zhuh/', 'tu': '/too/', 'il': '/eel/', 'elle': '/el/',
        'nous': '/noo/', 'vous': '/voo/', 'ils': '/eel/', 'elles': '/el/',
    };

    function getPhonetic(word) {
        return phoneticMap[word.toLowerCase()] || '/pronunciation guide unavailable/';
    }

    function updateWordDisplay(word) {
        currentWord = word;
        wordDisplay.textContent = word;
        phoneticDisplay.textContent = getPhonetic(word);
    }

    // Search
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && searchInput.value.trim()) {
            clearTimeout(window.searchTimeout); // ← cancel any pending debounce
            updateWordDisplay(searchInput.value.trim());
            searchInput.value = '';
        }
    });

    searchInput.addEventListener('input', () => {
        if (searchInput.value.trim()) {
            clearTimeout(window.searchTimeout);
            window.searchTimeout = setTimeout(() => {
                updateWordDisplay(searchInput.value.trim());
            }, 800);
        } else {
            // Restore last word when input is cleared
            clearTimeout(window.searchTimeout);
            updateWordDisplay(currentWord);
        }
    });

    // Audio button
    if (audioBtn_) {
        audioBtn_.addEventListener('click', () => {
            if (speechSynthesis.speaking) { speechSynthesis.cancel(); return; }
            const utterance = new SpeechSynthesisUtterance(currentWord);
            const voices = speechSynthesis.getVoices();
            const frenchVoice = voices.find(v => v.lang.startsWith('fr'));
            if (frenchVoice) utterance.voice = frenchVoice;
            utterance.lang = 'fr-FR';
            utterance.rate = 0.8;
            speechSynthesis.speak(utterance);
        });
    }

    // Record button
    if (recordBtn) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            recordBtn.disabled = true;
            recordBtn.title = 'Speech recognition not supported in this browser';
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.lang = 'fr-FR';
        recognition.interimResults = false;
        recognition.maxAlternatives = 3;

        let isRecording = false;

        recordBtn.addEventListener('click', () => {
            if (isRecording) {
                recognition.stop();
                return;
            }
            recognition.start();
        });

        recognition.onstart = () => {
            isRecording = true;
            recordBtn.innerHTML = '<span class="material-symbols-outlined">stop</span> Stop';
            recordBtn.classList.add('animate-pulse');
        };

        recognition.onend = () => {
            isRecording = false;
            recordBtn.innerHTML = '<span class="material-symbols-outlined">mic</span> Record';
            recordBtn.classList.remove('animate-pulse');
        };

        recognition.onresult = (event) => {
            const results = Array.from(event.results[0]).map(r => r.transcript.toLowerCase().trim());
            const target = currentWord.toLowerCase().trim();
            const matched = results.some(r => r === target || r.includes(target));

            showFeedback(matched, results[0]);
            
            if (matched) {
                wordsRecorded++;
                sessionStorage.setItem('words_recorded', wordsRecorded);
                updateGoal();
            }
        };

        recognition.onerror = (e) => {
            console.error('Recognition error:', e.error);
            showFeedback(null, null, e.error);
        };
    }

    // Feedback display
    function showFeedback(correct, heard, error = null) {
        // Remove existing feedback
        const existing = document.getElementById('pronunciationFeedback');
        if (existing) existing.remove();

        const container = document.querySelector('.border-dashed');
        const div = document.createElement('div');
        div.id = 'pronunciationFeedback';
        div.className = 'mt-4 p-4 rounded-xl text-center font-bold';

        if (error) {
            div.className += ' bg-yellow-50 text-yellow-700 border border-yellow-200';
            div.textContent = error === 'no-speech' ? '🔇 No speech detected. Try again!' : `⚠️ Error: ${error}`;
        } else if (correct) {
            div.className += ' bg-green-50 text-green-700 border border-green-200';
            div.textContent = `✅ Parfait! You said "${heard}" correctly!`;
        } else {
            div.className += ' bg-red-50 text-red-700 border border-red-200';
            div.textContent = `❌ You said "${heard}" — try again! Target: "${currentWord}"`;
        }

        container.insertAdjacentElement('afterend', div);
        setTimeout(() => div.remove(), 4000);
    }

    // Daily goal
    function updateGoal() {
        const goalBar = document.querySelector('.bg-accent.h-full');
        const goalText = document.querySelector('.text-accent\\/60');
        const goal = 20;
        const pct = Math.min((wordsRecorded / goal) * 100, 100);
        if (goalBar) goalBar.style.width = `${pct}%`;
        if (goalText) goalText.textContent = `${wordsRecorded}/${goal} Words recorded`;
    }

    updateGoal();
});