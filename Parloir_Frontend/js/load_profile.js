// Load user profile data across all pages
async function loadUserProfile() {
    try {
        const profileResult = await getProfile();
        
        if (profileResult && profileResult.success) {
            const { name, level, profile_picture } = profileResult.data;
            
            // Update all profile pictures on the page
            if (profile_picture) {
                const profileImages = document.querySelectorAll('img[alt*="User"], img[alt*="Profile"], img[alt*="Alexandre"], .w-10.h-10.rounded-full img, .w-8.h-8.rounded-full img');
                profileImages.forEach(img => {
                    img.src = profile_picture;
                });
            }
            
            // Update welcome messages
            const welcomeElements = document.querySelectorAll('#welcomeMessage, [id*="welcome"]');
            welcomeElements.forEach(el => {
                if (el && name) {
                    el.textContent = `Welcome, ${name}!`;
                }
            });
            
            return { name, level, profile_picture };
        }
    } catch (error) {
        console.error('Failed to load profile:', error);
    }
    
    return null;
}

// Auto-load on page load
if (isLoggedIn()) {
    document.addEventListener('DOMContentLoaded', loadUserProfile);
}