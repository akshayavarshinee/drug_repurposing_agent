const reportId = window.location.pathname.split('/').pop();

async function loadReport() {
    console.log('Loading report with ID:', reportId);
    const loadingDiv = document.getElementById('loading');
    const contentDiv = document.getElementById('reportContent');
    const errorDiv = document.getElementById('errorMessage');
    const loadingText = loadingDiv?.querySelector('p');
    
    try {
        console.log('Fetching report from:', `/api/results/${reportId}`);
        const response = await fetch(`/api/results/${reportId}`);
        console.log('Response status:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            
            document.getElementById('reportTitle').textContent = data.title;
            document.getElementById('reportQuestion').textContent = `Query: ${data.question}`;
            document.getElementById('reportDate').textContent = `Generated: ${new Date(data.created_at).toLocaleString()}`;
            
            const reportTextDiv = document.getElementById('reportText');
            reportTextDiv.innerHTML = marked.parse ? marked.parse(data.report_text) : data.report_text;
            
            loadingDiv.classList.add('hidden');
            contentDiv.classList.remove('hidden');
        } else if (response.status === 404) {
            // Report not found - might still be processing
            if (loadingText) {
                loadingText.textContent = 'Report is being generated... Please wait.';
            }
            
            // Poll for completion
            const pollInterval = setInterval(async () => {
                try {
                    const retryResponse = await fetch(`/api/results/${reportId}`);
                    if (retryResponse.ok) {
                        clearInterval(pollInterval);
                        location.reload(); // Reload to show the report
                    }
                } catch (pollError) {
                    console.error('Polling error:', pollError);
                }
            }, 5000); // Poll every 5 seconds
            
            // Stop polling after 10 minutes
            setTimeout(() => {
                clearInterval(pollInterval);
                loadingDiv.classList.add('hidden');
                errorDiv.textContent = 'Report generation is taking longer than expected. Please check back later.';
                errorDiv.classList.remove('hidden');
            }, 600000); // 10 minutes
            
        } else if (response.status === 401) {
            window.location.href = '/login';
        } else {
            loadingDiv.classList.add('hidden');
            errorDiv.textContent = 'Failed to load report';
            errorDiv.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error loading report:', error);
        loadingDiv.classList.add('hidden');
        errorDiv.textContent = 'An error occurred while loading the report';
        errorDiv.classList.remove('hidden');
    }
}

function downloadPDF() {
    alert('PDF download feature will be implemented in future updates');
}

loadReport();
