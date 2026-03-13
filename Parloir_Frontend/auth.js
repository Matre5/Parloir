// auth.js - protects pages that require login

function requireAuth() {

    if (!isLoggedIn()) {
        logout();
    }

}

// Run immediately
requireAuth();