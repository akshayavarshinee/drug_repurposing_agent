async function loadHistory() {
    const loadingDiv = document.getElementById('loading');
    const reportsListDiv = document.getElementById('reportsList');
    const emptyStateDiv = document.getElementById('emptyState');
    const errorDiv = document.getElementById('errorMessage');
    
    try {
        const response = await fetch('/api/results/');
        
        if (response.ok) {
            const reports = await response.json();
            
            loadingDiv.classList.add('hidden');
            
            if (reports.length === 0) {
                emptyStateDiv.classList.remove('hidden');
            } else {
                reportsListDiv.classList.remove('hidden');
                
                reports.forEach(report => {
                    const reportCard = document.createElement('div');
                    reportCard.className = 'bg-white rounded-lg shadow p-6 hover:shadow-lg transition cursor-pointer';
                    reportCard.onclick = () => window.location.href = `/results/${report.id}`;
                    
                    reportCard.innerHTML = `
                        <div class="flex justify-between items-start">
                            <div class="flex-1">
                                <h3 class="text-lg font-semibold mb-2">${report.title}</h3>
                                <p class="text-gray-600 mb-2">${report.question}</p>
                                <p class="text-sm text-gray-500">${new Date(report.created_at).toLocaleString()}</p>
                            </div>
                            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                            </svg>
                        </div>
                    `;
                    
                    reportsListDiv.appendChild(reportCard);
                });
            }
        } else {
            if (response.status === 401) {
                window.location.href = '/login';
            } else {
                loadingDiv.classList.add('hidden');
                errorDiv.textContent = 'Failed to load reports';
                errorDiv.classList.remove('hidden');
            }
        }
    } catch (error) {
        loadingDiv.classList.add('hidden');
        errorDiv.textContent = 'An error occurred while loading reports';
        errorDiv.classList.remove('hidden');
    }
}

loadHistory();
