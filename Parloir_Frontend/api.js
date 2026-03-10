// api.js - Handles all API calls to backend

const API_URL = 'http://localhost:8001/api';

// Register user (name, email, password)
async function register(name, email, password) {
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                email: email,
                password: password,
                // learning_style: 'patient_mentor',
                // level: 'A2'
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Registration failed');
        }

        // Save tokens and user info
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        localStorage.setItem('user_name', name);

        return { success: true, data: data };
    } catch (error) {
        console.error("Register error:", error); 
        return { success: false, error: error.message };
    }
}

// Login user (email, password)
async function login(email, password) {
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Invalid email or password');
        }

        // Save tokens and user info
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('user', JSON.stringify(data.user));

        return { success: true, data: data };
    } catch (error) {
        console.error("Login error:", error);
        return { success: false, error: error.message };
    }
}

async function refreshAccessToken() {
    const refreshToken = localStorage.getItem('refresh_token');

    if (!refreshToken) return false;

    try {
        const response = await fetch(`${API_URL}/auth/refresh`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                refresh_token: refreshToken
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error("Refresh failed");
        }

        localStorage.setItem("access_token", data.access_token);
        return true;

    } catch (error) {
        console.error("Token refresh error:", error);
        logout();
        return false;
    }
}

async function authFetch(url, options = {}) {

    options.headers = {
        ...(options.headers || {}),
        ...getAuthHeaders()
    };

    let response = await fetch(url, options);

    // If token expired
    if (response.status === 401) {

        const refreshed = await refreshAccessToken();

        if (refreshed) {
            options.headers = {
                ...(options.headers || {}),
                ...getAuthHeaders()
            };

            response = await fetch(url, options);
        } else {
            logout();
        }
    }

    return response;
}

// Logout user
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    localStorage.removeItem('user_name');
    window.location.href = 'login.html';
}

// Check if user is logged in
function isLoggedIn() {
    return localStorage.getItem('access_token') !== null;
}

// Get current user
function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

// Get user name
function getUserName() {
    return localStorage.getItem('user_name') || 'User';
}

function getAuthHeaders() {
    const token = localStorage.getItem("access_token");

    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}