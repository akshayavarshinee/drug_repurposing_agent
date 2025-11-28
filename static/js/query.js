document.getElementById('queryForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const question = formData.get('question');
    
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('errorMessage');
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const loadingText = loadingDiv.querySelector('p');
    
    loadingDiv.classList.remove('hidden');
    errorDiv.classList.add('hidden');
    submitBtn.disabled = true;
    
    try {
        // Submit the query
        const response = await fetch('/api/query/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            } else {
                errorDiv.textContent = data.detail || 'Failed to submit query';
                errorDiv.classList.remove('hidden');
                loadingDiv.classList.add('hidden');
                submitBtn.disabled = false;
                return;
            }
        }
        
        // Query submitted successfully, now poll for status
        const queryId = data.report_id; // This is actually the query ID
        loadingText.textContent = 'Processing your query with AI agents... This may take a few minutes.';
        
        // Poll every 3 seconds
        const pollInterval = setInterval(async () => {
            try {
                const statusResponse = await fetch(`/api/query/status/${queryId}`);
                const statusData = await statusResponse.json();
                
                if (statusData.status === 'completed') {
                    clearInterval(pollInterval);
                    // Find the report ID from the query
                    const reportsResponse = await fetch('/api/results/');
                    const reports = await reportsResponse.json();
                    const report = reports.find(r => r.query_id === queryId);
                    
                    if (report) {
                        window.location.href = `/results/${report.id}`;
                    } else {
                        errorDiv.textContent = 'Report generated but could not be loaded. Please check your reports list.';
                        errorDiv.classList.remove('hidden');
                        loadingDiv.classList.add('hidden');
                        submitBtn.disabled = false;
                    }
                } else if (statusData.status === 'failed') {
                    clearInterval(pollInterval);
                    errorDiv.textContent = `Query processing failed: ${statusData.error_message || 'Unknown error'}`;
                    errorDiv.classList.remove('hidden');
                    loadingDiv.classList.add('hidden');
                    submitBtn.disabled = false;
                } else {
                    // Still processing, update status message
                    loadingText.textContent = `Status: ${statusData.status}... Please wait.`;
                }
            } catch (pollError) {
                console.error('Status polling error:', pollError);
            }
        }, 3000); // Poll every 3 seconds
        
    } catch (error) {
        errorDiv.textContent = 'An error occurred. Please try again.';
        errorDiv.classList.remove('hidden');
        loadingDiv.classList.add('hidden');
        submitBtn.disabled = false;
    }
});
