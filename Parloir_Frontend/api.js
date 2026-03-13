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
        localStorage.setItem('user_name', data.user.name);

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

// Get user profile
async function getProfile() {
    try {
        const response = await authFetch(`${API_URL}/profile/me`, {
            method: 'GET'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to get profile');
        }

        return { success: true, data: data };
    } catch (error) {
        console.error("Get profile error:", error);
        return { success: false, error: error.message };
    }
}

// Update user profile
async function updateProfile(name, learningStyle, level) {
    try {
        const updateData = {};
        if (name !== undefined) updateData.name = name;
        if (learningStyle !== undefined) updateData.learning_style = learningStyle;
        if (level !== undefined) updateData.level = level;

        const response = await authFetch(`${API_URL}/profile/me`, {
            method: 'PUT',
            body: JSON.stringify(updateData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to update profile');
        }

        // Update localStorage
        if (name) localStorage.setItem('user_name', name);
        
        const user = getCurrentUser();
        if (user) {
            if (name) user.name = name;
            if (learningStyle) user.learning_style = learningStyle;
            if (level) user.level = level;
            localStorage.setItem('user', JSON.stringify(user));
        }

        return { success: true, data: data };
    } catch (error) {
        console.error("Update profile error:", error);
        return { success: false, error: error.message };
    }
}

// Upload profile picture
async function uploadProfilePicture(file) {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const token = localStorage.getItem('access_token');
        
        const response = await fetch(`${API_URL}/profile/upload-picture`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData  // Don't set Content-Type, browser will set it with boundary
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to upload image');
        }

        return { success: true, url: data.url };
    } catch (error) {
        console.error("Upload picture error:", error);
        return { success: false, error: error.message };
    }
}

function parseJwt(token) {
    try {
        return JSON.parse(atob(token.split('.')[1]));
    } catch (e) {
        return null;
    }
}

// Translate text
async function translate(text, sourceLang, targetLang) {
    try {
        const response = await authFetch(`${API_URL}/translate/`, {
            method: 'POST',
            body: JSON.stringify({
                text: text,
                source_lang: sourceLang,
                target_lang: targetLang
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Translation failed');
        }

        return { success: true, data: data };
    } catch (error) {
        console.error("Translation error:", error);
        return { success: false, error: error.message };
    }
}

// Word List Functions

// Add word to list
async function addWord(word, translation, context = null, source = 'manual') {
    try {
        const response = await authFetch(`${API_URL}/words/add`, {
            method: 'POST',
            body: JSON.stringify({
                word: word,
                translation: translation,
                context: context,
                source: source
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to add word');
        }

        return { success: true, data: data };
    } catch (error) {
        console.error("Add word error:", error);
        return { success: false, error: error.message };
    }
}

// Get word list
async function getWords(status = null, search = null) {
    try {
        let url = `${API_URL}/words/list`;
        const params = new URLSearchParams();
        
        if (status) params.append('status', status);
        if (search) params.append('search', search);
        
        if (params.toString()) {
            url += `?${params.toString()}`;
        }

        const response = await authFetch(url, {
            method: 'GET'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to get words');
        }

        return { success: true, data: data };
    } catch (error) {
        console.error("Get words error:", error);
        return { success: false, error: error.message };
    }
}

// Update word
async function updateWord(wordId, status = null, notes = null) {
    try {
        const updateData = {};
        if (status) updateData.status = status;
        if (notes !== null) updateData.notes = notes;

        const response = await authFetch(`${API_URL}/words/${wordId}`, {
            method: 'PUT',
            body: JSON.stringify(updateData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to update word');
        }

        return { success: true, data: data };
    } catch (error) {
        console.error("Update word error:", error);
        return { success: false, error: error.message };
    }
}

// Delete word
async function deleteWord(wordId) {
    try {
        const response = await authFetch(`${API_URL}/words/${wordId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to delete word');
        }

        return { success: true, data: data };
    } catch (error) {
        console.error("Delete word error:", error);
        return { success: false, error: error.message };
    }
}

// Get word stats
async function getWordStats() {
    try {
        const response = await authFetch(`${API_URL}/words/stats`, {
            method: 'GET'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to get stats');
        }

        return { success: true, data: data };
    } catch (error) {
        console.error("Get stats error:", error);
        return { success: false, error: error.message };
    }
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
    // return localStorage.getItem('access_token') !== null;
    const token = localStorage.getItem('access_token');

    if (!token) return false;

    const decoded = parseJwt(token);

    if (!decoded) return false;

    const now = Date.now() / 1000;

    return decoded.exp > now;
}

// Get current user
function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

// Get user name
function getUserName() {
    const user = getCurrentUser();
    return user?.name || 'User';
}

function getAuthHeaders() {
    const token = localStorage.getItem("access_token");

    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}