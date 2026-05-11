// Auth check
if (!isLoggedIn()) {
    window.location.href = 'login.html';
}

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Translate page loaded');
    
    // State
    let currentSourceLang = 'en';
    let currentTargetLang = 'fr';
    
    // DOM elements - FIXED SELECTORS
    const sourceTextarea = document.querySelector('textarea');
    const translatedOutput = document.querySelector('.text-accent-green');
    const charCount = document.querySelector('.text-primary\\/40');
    
    // Get language labels
    const langLabels = document.querySelectorAll('.heavy-border.px-6.py-2');
    const sourceLangLabel = langLabels[0];
    const targetLangLabel = langLabels[1];
    
    // Get all buttons
    const allButtons = document.querySelectorAll('button');
    
    // Find swap button (has swap_horiz icon)
    let swapBtn = null;
    allButtons.forEach(btn => {
        const icon = btn.querySelector('.material-symbols-outlined');
        if (icon && icon.textContent.trim() === 'swap_horiz') {
            swapBtn = btn;
        }
    });
    
    // Find copy button (has content_copy icon)
    let copyBtn = null;
    allButtons.forEach(btn => {
        const icon = btn.querySelector('.material-symbols-outlined');
        if (icon && icon.textContent.trim() === 'content_copy') {
            copyBtn = btn;
        }
    });

    // Listen button
    let listenBtn = null;
    allButtons.forEach(btn => {
        const icon = btn.querySelector('.material-symbols-outlined');
        if (icon && icon.textContent.trim() === 'volume_up') {
            listenBtn = btn;
        }
    });

    if (listenBtn) {
        listenBtn.addEventListener('click', () => {
            const text = translatedOutput.textContent;
            if (!text || text === 'Le texte traduit apparaîtra ici...') return;
            
            if (speechSynthesis.speaking) { speechSynthesis.cancel(); return; }
            
            const utterance = new SpeechSynthesisUtterance(text.split('\n\n📢')[0]);
            const voices = speechSynthesis.getVoices();
            const frenchVoice = voices.find(v => v.lang.startsWith('fr'));
            if (frenchVoice) utterance.voice = frenchVoice;
            utterance.lang = 'fr-FR';
            utterance.rate = 0.9;
            speechSynthesis.speak(utterance);
        });
    }
    
    // Save to word list
    let saveBtn = null;
    allButtons.forEach(btn => {
        if (btn.textContent.includes('SAVE TO WORD LIST') || btn.textContent.includes('Save to Word List')) {
            saveBtn = btn;
        }
    });

    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            const sourceText = sourceTextarea.value.trim();
            const translatedText = translatedOutput.textContent.split('\n\n📢')[0].trim();
            
            if (!sourceText || !translatedText || 
                translatedText === 'Le texte traduit apparaîtra ici...' ||
                translatedText === 'Translating...') {
                alert('Please translate something first!');
                return;
            }
            
            const result = await addWord(sourceText, translatedText, null, 'translator');
            
            if (result.success) {
                saveBtn.textContent = '✅ Saved!';
                setTimeout(() => {
                    saveBtn.innerHTML = '<span class="material-symbols-outlined">bookmark</span> SAVE TO WORD LIST';
                }, 2000);
            } else {
                alert('Failed to save: ' + result.error);
            }
        });
    }

    console.log('Elements found:', {
        sourceTextarea: !!sourceTextarea,
        translatedOutput: !!translatedOutput,
        swapBtn: !!swapBtn,
        copyBtn: !!copyBtn
    });
    
    // Update character count
    if (sourceTextarea && charCount) {
        sourceTextarea.addEventListener('input', () => {
            const count = sourceTextarea.value.length;
            charCount.textContent = `${count} / 5000`;
            
            console.log('Text changed:', count, 'chars');
            
            // Auto-translate after user stops typing (debounce)
            clearTimeout(window.translateTimeout);
            if (count > 0) {
                window.translateTimeout = setTimeout(() => {
                    performTranslation();
                }, 1000);
            } else {
                // Clear translation if text is empty
                translatedOutput.textContent = 'Le texte traduit apparaîtra ici...';
            }
        });
    }
    
    // Swap languages
    if (swapBtn) {
        swapBtn.addEventListener('click', () => {
            console.log('Swapping languages');
            
            // Swap languages
            [currentSourceLang, currentTargetLang] = [currentTargetLang, currentSourceLang];
            
            // Update labels
            sourceLangLabel.textContent = currentSourceLang === 'en' ? 'English' : 'French';
            targetLangLabel.textContent = currentTargetLang === 'fr' ? 'French' : 'English';
            
            // Swap text
            const sourceText = sourceTextarea.value;
            const translatedText = translatedOutput.textContent;
            
            if (translatedText !== 'Le texte traduit apparaîtra ici...' && 
                translatedText !== 'Translated text will appear here...') {
                sourceTextarea.value = translatedText.split('\n\n📢')[0]; // Remove pronunciation if present
            }
            
            // Re-translate
            if (sourceTextarea.value.trim()) {
                performTranslation();
            } else {
                translatedOutput.textContent = currentTargetLang === 'fr' ? 
                    'Le texte traduit apparaîtra ici...' : 
                    'Translated text will appear here...';
            }
        });
    }
    
    // Copy translation
    if (copyBtn) {
        copyBtn.addEventListener('click', async () => {
            const text = translatedOutput.textContent;
            
            if (text && text !== 'Le texte traduit apparaîtra ici...' && 
                text !== 'Translated text will appear here...' && 
                text !== 'Translating...') {
                try {
                    // Remove pronunciation guide before copying
                    const textToCopy = text.split('\n\n📢')[0];
                    await navigator.clipboard.writeText(textToCopy);
                    
                    console.log('Copied to clipboard');
                    
                    // Visual feedback
                    const textSpan = copyBtn.querySelector('span:not(.material-symbols-outlined)');
                    if (textSpan) {
                        const originalText = textSpan.textContent;
                        textSpan.textContent = 'Copied!';
                        setTimeout(() => {
                            textSpan.textContent = originalText;
                        }, 2000);
                    }
                } catch (err) {
                    console.error('Failed to copy:', err);
                    alert('Failed to copy. Please select and copy manually.');
                }
            }
        });
    }
    
    // Perform translation
    async function performTranslation() {
        const text = sourceTextarea.value.trim();
        
        if (!text) return;
        
        console.log('Translating:', text, 'from', currentSourceLang, 'to', currentTargetLang);
        
        // Show loading
        translatedOutput.textContent = 'Translating...';
        translatedOutput.classList.add('animate-pulse');
        
        // Call API
        const result = await translate(text, currentSourceLang, currentTargetLang);
        
        translatedOutput.classList.remove('animate-pulse');
        
        console.log('Translation result:', result);
        
        if (result.success) {
            let displayText = result.data.translated_text;
            
            // Add pronunciation if available
            if (result.data.pronunciation && currentTargetLang === 'fr') {
                displayText += `\n\n📢 Pronunciation: ${result.data.pronunciation}`;
            }
            
            translatedOutput.textContent = displayText;
            translatedOutput.classList.remove('text-red-500');
        } else {
            translatedOutput.textContent = '❌ Translation failed: ' + (result.error || 'Unknown error');
            translatedOutput.classList.add('text-red-500');
        }
    }
    
    // Initial placeholder based on target language
    translatedOutput.textContent = currentTargetLang === 'fr' ? 
        'Le texte traduit apparaîtra ici...' : 
        'Translated text will appear here...';

    // Auto-fill from comprehension page
    const urlParams = new URLSearchParams(window.location.search);
    const prefilledWord = urlParams.get('word');
    if (prefilledWord) {
        sourceTextarea.value = prefilledWord;
        charCount.textContent = `${prefilledWord.length} / 5000`;
        currentSourceLang = 'fr';
        currentTargetLang = 'en';
        sourceLangLabel.textContent = 'French';
        targetLangLabel.textContent = 'English';
        performTranslation();
    }
});