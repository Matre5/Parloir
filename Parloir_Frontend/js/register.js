// CONFIG
const API_BASE_URL = 'http://localhost:8001/api';

// CHECK IF ALREADY LOGGED IN
if (localStorage.getItem('access_token')) {
    window.location.href = 'index.html';
}

// FORM ELEMENTS
const registerForm = document.getElementById('registerForm');
const usernameInput = document.getElementById('username');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const confirmPasswordInput = document.getElementById('confirmPassword');
const levelSelect = document.getElementById('level');
const registerButton = document.getElementById('registerButton');

// HANDLE REGISTRATION
async function handleRegister(e) {
    e.preventDefault();
    
    const username = usernameInput.value.trim();
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;
    const level = levelSelect.value;

    // Validation
    if (!username || !email || !password || !confirmPassword) {
        alert('❌ Veuillez remplir tous les champs');
        return;
    }

    if (password !== confirmPassword) {
        alert('❌ Les mots de passe ne correspondent pas');
        return;
    }

    if (password.length < 6) {
        alert('❌ Le mot de passe doit contenir au moins 6 caractères');
        return;
    }

    // Show loading state
    registerButton.disabled = true;
    registerButton.textContent = 'Inscription en cours...';

    try {
        const res = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                username, 
                email, 
                password, 
                level 
            })
        });

        const data = await res.json();

        if (res.ok) {
            // Success! Redirect to verification page
            console.log('✅ Registration successful:', data);
            window.location.href = `email-verification-sent.html?email=${encodeURIComponent(email)}`;
        } else {
            // Error from backend
            alert('❌ ' + data.detail);
            registerButton.disabled = false;
            registerButton.textContent = 'S\'inscrire';
        }
    } catch (err) {
        console.error('Registration error:', err);
        alert('❌ Erreur de connexion au serveur. Veuillez réessayer.');
        registerButton.disabled = false;
        registerButton.textContent = 'S\'inscrire';
    }
}

// EVENT LISTENERS
if (registerForm) {
    registerForm.addEventListener('submit', handleRegister);
}

// Optional: Real-time password match validation
if (confirmPasswordInput) {
    confirmPasswordInput.addEventListener('input', () => {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        if (confirmPassword && password !== confirmPassword) {
            confirmPasswordInput.style.borderColor = '#ef4444';
        } else {
            confirmPasswordInput.style.borderColor = '';
        }
    });
}