// // Check if user is logged in
// if (!isLoggedIn()) {
// window.location.href = "login.html";
// }

// // User is logged in - get their info
// const user = getCurrentUser();
// const userName = getUserName();

// console.log("Logged in as:", user);
// console.log("User name:", userName);

// document.addEventListener("DOMContentLoaded", function () {
// // Try multiple sources for the name
// const storedName = localStorage.getItem("user_name");
// const user = getCurrentUser();
// const userEmail = user?.email || "";
// const emailName = userEmail.split("@")[0];

// // Use stored name first, then email username, then 'User'
// const displayName = storedName || emailName || "User";

// const welcomeEl = document.getElementById("welcomeMessage");
// if (welcomeEl) {
//     welcomeEl.textContent = `Welcome, ${displayName}!`;
// }

// console.log("Display name:", displayName);
// console.log("Stored name:", storedName);
// console.log("User:", user);
// });

// Check if user is logged in
// Check if user is logged in
if (!isLoggedIn()) {
    window.location.href = "login.html";
}

document.addEventListener("DOMContentLoaded", async function () {
    // Try to get profile from backend first
    const profileResult = await getProfile();
    
    let displayName = "User";
    let userLevel = "A2";
    let userStyle = "patient_mentor";
    
    if (profileResult && profileResult.success) {
        displayName = profileResult.data.name || "User";
        userLevel = profileResult.data.level || "A2";
        userStyle = profileResult.data.learning_style || "patient_mentor";
        
        // Update profile picture if exists
        if (profileResult.data.profile_picture) {
            const profileImgs = document.querySelectorAll('img[alt*="Alexandre"], img[alt*="User"]');
            profileImgs.forEach(img => {
                img.src = profileResult.data.profile_picture;
            });
        }
    } else {
        // Fallback to localStorage
        const storedName = localStorage.getItem("user_name");
        const user = getCurrentUser();
        const userEmail = user?.email || "";
        const emailName = userEmail.split("@")[0];
        
        displayName = storedName || emailName || "User";
    }

    // Update welcome message
    const welcomeEl = document.getElementById("welcomeMessage");
    if (welcomeEl) {
        welcomeEl.textContent = `Welcome, ${displayName}!`;
    }

    // Update level badge
    const levelBadge = document.querySelector('.bg-secondary.text-white');
    if (levelBadge) {
        levelBadge.textContent = `Level ${userLevel}`;
    }

    // Update level description
    const levelDesc = document.querySelector('.text-slate-400.text-sm');
    if (levelDesc) {
        const levelDescriptions = {
            'A1': 'Beginner',
            'A2': 'Elementary',
            'B1': 'Intermediate',
            'B2': 'Upper Intermediate',
            'C1': 'Advanced',
            'C2': 'Proficient'
        };
        levelDesc.textContent = levelDescriptions[userLevel] || 'Advanced Intermediate';
    }

    console.log("Profile loaded:", { displayName, userLevel, userStyle });
});