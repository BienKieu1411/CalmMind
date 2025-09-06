const API_BASE_URL = '/api';

async function callBackendAPI(text) {
    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.detail || `HTTP error! status: ${response.status}`;
            throw new Error(errorMessage);
        }
        return await response.json();
    } catch (error) {
        console.error('Backend API error:', error);
        throw error;
    }
}

async function analyzeMentalHealth() {
    const userInput = document.getElementById('userInput').value.trim();
    
    if (!userInput) {
        const errorDiv = document.getElementById('inputError');
        errorDiv.textContent = "🌱 You haven't shared your feelings yet. Please tell us how you're feeling so we can support you!";
        errorDiv.style.display = "block";
        document.getElementById('results').style.display = "none";
        return;
    } else {
        document.getElementById('inputError').style.display = "none";
    }

    document.getElementById('analyzeBtn').disabled = true;
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';

    try {
        const response = await callBackendAPI(userInput);
        displayResults(response.classification, response.suggestions);
    } catch (error) {
        console.error('Analysis error:', error);
        displayError('An error occurred during analysis. Please try again later.');
    } finally {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('analyzeBtn').disabled = false;
    }
}

function displayResults(classification, suggestions) {
    document.getElementById('classificationLabel').textContent = classification;
    document.getElementById('classificationDescription').textContent = `Classification: ${classification}`;
    document.getElementById('suggestionText').innerHTML = suggestions;
    document.getElementById('results').style.display = 'block';
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

function displayError(message) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `
        <div class="result-card error">
            <div class="result-title">
                <svg class="icon" viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
                Error
            </div>
            <div class="result-content">${message}</div>
        </div>
    `;
    resultsDiv.style.display = 'block';
}

document.getElementById('analyzeBtn').addEventListener('click', analyzeMentalHealth);

document.getElementById('userInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) analyzeMentalHealth();
});

document.getElementById('userInput').addEventListener('input', function() {
    const maxHeight = 300;
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, maxHeight) + 'px';
    document.getElementById('results').style.display = 'none';
});

document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const exampleTabs = document.querySelectorAll('.examples-tab');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetLang = this.getAttribute('data-lang');
            tabButtons.forEach(btn => btn.classList.remove('active'));
            exampleTabs.forEach(tab => tab.classList.remove('active'));
            this.classList.add('active');
            document.getElementById(`examples-${targetLang}`).classList.add('active');
        });
    });

    const exampleItems = document.querySelectorAll('.example-item');
    const userInput = document.getElementById('userInput');

    exampleItems.forEach(item => {
        item.addEventListener('click', function() {
            const exampleText = this.getAttribute('data-text');
            userInput.value = exampleText;
            userInput.style.height = 'auto';
            userInput.style.height = Math.min(userInput.scrollHeight, 300) + 'px';
            document.getElementById('results').style.display = 'none';
            userInput.focus();
            analyzeMentalHealth();
        });
    });
});