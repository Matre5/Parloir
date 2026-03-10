// auth.js - protects pages that require login

function requireAuth() {
    const token = localStorage.getItem('access_token');

    if (!token) {
        window.location.href = 'login.html';
    }
}

// Run immediately
requireAuth();