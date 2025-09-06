// Backend API configuration - auto-detect URL for Vercel deployment
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000' 
    : '';

// Function to call the backend API
async function callBackendAPI(text) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
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
        const results = document.querySelector(".results");
        results.style.display = "none";
        return;
    } else {
        document.getElementById('inputError').style.display = "none";
    }

    document.getElementById('analyzeBtn').disabled = true;
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';

    try {
        // Call the backend API
        const response = await callBackendAPI(userInput);
        
        // Extract data from backend response
        const userLanguage = response.user_language;
        const englishText = response.translated_text;
        const classification = response.classification;
        const suggestions = response.suggestions;

        displayResults(userLanguage, englishText, classification, suggestions);

    } catch (error) {
        console.error('Analysis error:', error);
        displayError('An error occurred during analysis. Please make sure the backend server is running on port 8000.');
    } finally {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('analyzeBtn').disabled = false;
    }
}

function displayResults(userLanguage, englishText, classification, suggestions) {
    if (userLanguage !== 'en') {
        document.getElementById('translationResult').style.display = 'block';
        document.getElementById('translatedText').textContent = englishText;
    } else {
        document.getElementById('translationResult').style.display = 'none';
    }

    // Handle classification - it's now a string, not an object
    document.getElementById('classificationLabel').textContent = classification;
    document.getElementById('classificationDescription').textContent = 
        `Classification: ${classification}`;

    // Use innerHTML to render HTML line breaks
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
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        analyzeMentalHealth();
    }
});

document.getElementById('userInput').addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
});

// Examples functionality
document.addEventListener('DOMContentLoaded', function() {
    // Language tab switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    const exampleTabs = document.querySelectorAll('.examples-tab');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetLang = this.getAttribute('data-lang');
            
            // Remove active class from all tabs and buttons
            tabButtons.forEach(btn => btn.classList.remove('active'));
            exampleTabs.forEach(tab => tab.classList.remove('active'));
            
            // Add active class to clicked button and corresponding tab
            this.classList.add('active');
            document.getElementById(`examples-${targetLang}`).classList.add('active');
        });
    });
    
    // Example item selection
    const exampleItems = document.querySelectorAll('.example-item');
    const userInput = document.getElementById('userInput');
    
    exampleItems.forEach(item => {
        item.addEventListener('click', function() {
            const exampleText = this.getAttribute('data-text');
            userInput.value = exampleText;
            userInput.style.height = 'auto';
            userInput.style.height = userInput.scrollHeight + 'px';
            
            // Add visual feedback
            this.style.background = '#e8f4fd';
            this.style.borderColor = '#667eea';
            
            // Remove feedback after a short delay
            setTimeout(() => {
                this.style.background = '';
                this.style.borderColor = '';
            }, 1000);
            
            // Focus on textarea
            userInput.focus();
        });
    });
});