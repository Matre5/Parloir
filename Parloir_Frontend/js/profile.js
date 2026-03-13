document.addEventListener('DOMContentLoaded', function() {
    let currentProfilePicture = null;
    
    // Profile modal functions
    window.openProfileModal = async function() {
        const modal = document.getElementById('profileModal');
        const result = await getProfile();
        
        if (result.success) {
            document.getElementById('profileName').value = result.data.name || '';
            document.getElementById('profileLevel').value = result.data.level || 'A2';
            document.getElementById('profileStyle').value = result.data.learning_style || 'patient_mentor';
            
            // Set profile picture
            if (result.data.profile_picture) {
                document.getElementById('profilePreview').src = result.data.profile_picture;
                currentProfilePicture = result.data.profile_picture;
            }
        }
        
        modal.classList.remove('hidden');
    };
    
    window.closeProfileModal = function() {
        document.getElementById('profileModal').classList.add('hidden');
    };
    
    // Handle image selection
    document.getElementById('profilePictureInput').addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        // Validate file size (5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('❌ Image too large! Max 5MB');
            return;
        }
        
        // Preview image
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('profilePreview').src = e.target.result;
        };
        reader.readAsDataURL(file);
        
        // Upload to server
        const uploadBtn = document.querySelector('#profileForm button[type="submit"]');
        uploadBtn.textContent = 'Uploading...';
        uploadBtn.disabled = true;
        
        const result = await uploadProfilePicture(file);
        
        uploadBtn.textContent = 'Save Changes';
        uploadBtn.disabled = false;
        
        if (result.success) {
            currentProfilePicture = result.url;
            alert('✅ Picture uploaded!');
        } else {
            alert('❌ Upload failed: ' + result.error);
        }
    });
    
    // Handle profile form submission
    document.getElementById('profileForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('profileName').value;
        const level = document.getElementById('profileLevel').value;
        const style = document.getElementById('profileStyle').value;
        
        const result = await updateProfile(name, style, level);
        
        if (result.success) {
            alert('✅ Profile updated!');
            closeProfileModal();
            
            // Update welcome message
            const welcomeEl = document.getElementById('welcomeMessage');
            if (welcomeEl) {
                welcomeEl.textContent = `Welcome, ${name}!`;
            }
            
            // Reload page to show new picture everywhere
            location.reload();
        } else {
            alert('❌ Failed to update profile: ' + result.error);
        }
    });
});