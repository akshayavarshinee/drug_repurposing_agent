async function logout() {
    try {
        const response = await fetch('/auth/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            window.location.href = data.redirect || '/';
        }
    } catch (error) {
        console.error('Logout error:', error);
        window.location.href = '/';
    }
}

document.getElementById('fileInput')?.addEventListener('change', function(e) {
    const fileText = document.getElementById('fileText');
    if (fileText) {
        if (this.files.length > 0) {
            fileText.textContent = this.files[0].name;
        } else {
            fileText.textContent = 'No file chosen';
        }
    }
});
