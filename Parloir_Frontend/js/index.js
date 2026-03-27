// Auth check
if (!isLoggedIn()) {
    window.location.href = 'login.html';
}

document.addEventListener('DOMContentLoaded', async function() {
    console.log('Index page loaded');
    
    // Load all dashboard data
    await loadUserProfile();
    await loadTodayEssay();
    await loadRecentWords();
    
    // Event listeners
    const chatBtn = document.getElementById('chatWithTutorBtn');
    if (chatBtn) {
        chatBtn.addEventListener('click', () => {
            window.location.href = 'chat_room.html';
        });
    }
    
    const editProfileBtn = document.getElementById('editProfileBtn');
    if (editProfileBtn) {
        editProfileBtn.addEventListener('click', () => {
            window.location.href = 'profile.html';
        });
    }
});

// Load user profile and stats
async function loadUserProfile() {
    const result = await getProfile();
    
    if (result.success) {
        const profile = result.data;
        
        // Update welcome message
        const userName = document.getElementById('userName');
        if (userName) {
            userName.textContent = profile.name;
        }
        
        // Update level badge
        const userLevel = document.getElementById('userLevel');
        if (userLevel) {
            userLevel.textContent = `Niveau ${profile.level}`;
        }
        
        // Update level description
        const levelDesc = document.getElementById('levelDesc');
        if (levelDesc) {
            const levelDescriptions = {
                'A1': 'Beginner',
                'A2': 'Elementary',
                'B1': 'Intermediate',
                'B2': 'Advanced Intermediate',
                'C1': 'Advanced',
                'C2': 'Mastery'
            };
            levelDesc.textContent = levelDescriptions[profile.level] || 'Intermediate';
        }
        
        // Update profile picture
        const profilePic = document.getElementById('profilePicture');
        if (profilePic && profile.profile_picture_url) {
            profilePic.style.backgroundImage = `url("${profile.profile_picture_url}")`;
            profilePic.style.backgroundSize = 'cover';
            profilePic.style.backgroundPosition = 'center';
        }
        
        // Update streak and XP (placeholders for now)
        updateStreak(15);
        updateXP(150, 200);
    } else {
        console.error('Failed to load profile:', result.error);
    }
}

// Load today's essay prompt for user's level
async function loadTodayEssay() {
    const result = await getEssayPrompts();
    
    if (result.success) {
        const prompts = result.data;
        
        // Find user's level prompt (marked with is_current_level)
        const userPrompt = prompts.find(p => p.is_current_level);
        
        if (userPrompt) {
            displayTodayEssay(userPrompt);
        } else {
            console.log('No user-level prompt found, using first prompt');
            if (prompts.length > 0) {
                displayTodayEssay(prompts[0]);
            }
        }
        
        // Display all prompts (first 3)
        displayAllPrompts(prompts);
    } else {
        console.error('Failed to load essays:', result.error);
    }
}

// Display today's highlighted essay
function displayTodayEssay(prompt) {
    const container = document.getElementById('todayEssayContainer');
    
    if (!container) {
        console.log('todayEssayContainer not found');
        return;
    }
    
    const categoryLabels = {
        'personal': 'CULTURE & SOCIETY',
        'narrative': 'GRAMMAR FOCUS',
        'opinion': 'OPINION',
        'argumentative': 'CULTURE & SOCIETY',
        'synthesis': 'SYNTHESIS',
        'critical': 'CRITICAL THINKING'
    };
    
    const categoryLabel = categoryLabels[prompt.category] || 'ESSAY';
    
    container.innerHTML = `
        <div class="flex items-center justify-between mb-3">
            <span class="text-[10px] font-bold text-secondary uppercase tracking-[0.2em]">
                ${categoryLabel}
            </span>
            <span class="text-[10px] font-bold text-white bg-accent-2 px-3 py-1 rounded-full">
                New
            </span>
        </div>
        <h3 class="text-2xl font-bold text-slate-900 mb-3 italic">
            "${escapeHtml(prompt.title)}"
        </h3>
        <p class="text-sm text-slate-500 mb-4">
            ${escapeHtml(prompt.description)}
        </p>
        <button onclick="window.location.href='essays.html'" 
                class="flex items-center gap-2 text-primary hover:text-secondary font-bold group">
            <span>Start Writing</span>
            <span class="text-xl group-hover:translate-x-1 transition-transform">→</span>
        </button>
    `;
}

// Display all level prompts (first 3)
function displayAllPrompts(prompts) {
    const container = document.getElementById('allPromptsContainer');
    
    if (!container) {
        console.log('allPromptsContainer not found');
        return;
    }
    
    // Show first 3 prompts
    const displayPrompts = prompts.slice(0, 3);
    
    const categoryColors = {
        'personal': 'bg-secondary/10 text-secondary',
        'narrative': 'bg-accent-1/10 text-accent-1',
        'opinion': 'bg-primary/10 text-primary',
        'argumentative': 'bg-secondary/10 text-secondary',
        'synthesis': 'bg-accent-2/10 text-accent-2',
        'critical': 'bg-accent-1/10 text-accent-1'
    };
    
    const categoryLabels = {
        'personal': 'CULTURE & SOCIETY',
        'narrative': 'GRAMMAR FOCUS',
        'opinion': 'OPINION',
        'argumentative': 'CULTURE & SOCIETY',
        'synthesis': 'SYNTHESIS',
        'critical': 'ENVIRONMENT'
    };
    
    container.innerHTML = displayPrompts.map(prompt => {
        const colorClass = categoryColors[prompt.category] || 'bg-slate-100 text-slate-600';
        const categoryLabel = categoryLabels[prompt.category] || 'ESSAY';
        
        return `
            <div class="group p-6 border-2 border-slate-100 hover:border-accent-2 transition-all cursor-pointer rounded-3xl"
                 onclick="window.location.href='essays.html'">
                <span class="text-[10px] font-bold ${colorClass} px-3 py-1 rounded-full uppercase tracking-[0.2em] inline-block mb-3">
                    ${categoryLabel}
                </span>
                <h4 class="text-lg font-bold text-slate-900 group-hover:text-primary transition-colors italic mb-2">
                    "${escapeHtml(prompt.title)}"
                </h4>
                <p class="text-sm text-slate-500 mb-3">
                    ${escapeHtml(prompt.description)}
                </p>
                <div class="flex items-center gap-2 text-primary group-hover:text-secondary transition-colors">
                    <span class="text-sm font-bold">View Prompt</span>
                    <span class="text-xl group-hover:translate-x-1 transition-transform">→</span>
                </div>
            </div>
        `;
    }).join('');
}

// Load recent words
async function loadRecentWords() {
    const result = await getWords(null, null);
    
    if (result.success) {
        const words = result.data.slice(0, 3);
        displayRecentWords(words);
    } else {
        console.error('Failed to load words:', result.error);
    }
}

// Display recent words
function displayRecentWords(words) {
    const container = document.getElementById('recentWordsContainer');
    
    if (!container) {
        console.log('recentWordsContainer not found');
        return;
    }
    
    if (words.length === 0) {
        container.innerHTML = `
            <p class="text-sm text-slate-500 text-center py-4">
                No words saved yet. Start adding words from the Translator!
            </p>
        `;
        return;
    }
    
    container.innerHTML = words.map(word => `
        <div class="flex items-center justify-between py-3 border-b border-slate-100 last:border-0">
            <div>
                <h4 class="font-bold text-primary">${escapeHtml(word.word)}</h4>
                <p class="text-sm text-slate-500 italic">${escapeHtml(word.translation)}</p>
            </div>
            <button class="text-accent-2 hover:text-accent-1" onclick="removeWord('${word.id}')">
                <span class="text-xl">×</span>
            </button>
        </div>
    `).join('');
}

// Update streak display
function updateStreak(days) {
    const streakDays = document.getElementById('streakDays');
    if (streakDays) {
        streakDays.textContent = days;
    }
}

// Update XP display
function updateXP(current, total) {
    const xpText = document.getElementById('xpText');
    const xpProgress = document.getElementById('xpProgress');
    const xpPercentage = document.getElementById('xpPercentage');
    
    if (xpText) {
        xpText.textContent = `${current} / ${total} XP`;
    }
    
    const percentage = Math.round((current / total) * 100);
    
    if (xpProgress) {
        xpProgress.style.width = `${percentage}%`;
    }
    
    if (xpPercentage) {
        xpPercentage.textContent = `${percentage}%`;
    }
}

// Remove word
window.removeWord = async function(wordId) {
    const result = await deleteWord(wordId);
    
    if (result.success) {
        await loadRecentWords();
    } else {
        alert('Failed to remove word');
    }
};

// Helper function
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}