# 🌱 CalmMind - Mental Health Analysis Platform

CalmMind is an intelligent mental health analysis platform that uses AI to understand emotions and provide personalized mental health care recommendations.

## Overview

CalmMind allows users to share their emotions and thoughts through a friendly web interface. The system will:

- **Detect language** and automatically translate to English if needed
- **Classify mental health conditions** using a trained BERT model
- **Provide personalized suggestions** based on AI analysis
- **Beautiful interface** with user-friendly and intuitive design

## System Architecture

The project is divided into 3 main components:

```
CalmMind/
├── client/          # Frontend (HTML, CSS, JavaScript)
├── api/          # Backend API (FastAPI)
├── requirements.txt # Python dependencies
└── mental-health.ipynb  # ML Model (BERT Classification)
```

### Frontend (Client)
- Pure **HTML/CSS/JavaScript**
- Responsive and user-friendly interface
- Integration with backend API
- Visual display of analysis results

### Backend (Server)
- **FastAPI** framework
- `/analyze` API endpoint for processing requests
- Integration with ML model via Gradio
- Multi-language translation
- Generate suggestions using Groq LLM

## Machine Learning Model

### Dataset
- Uses "Sentiment Analysis for Mental Health" dataset
- Dataset link: `https://www.kaggle.com/datasets/suchintikasarkar/sentiment-analysis-for-mental-health`
- Includes labeled psychological state statements
- Preprocessed and cleaned data

### Model
- **BERT-base-uncased** as backbone
- Fine-tuned for classification task
- Handles class imbalance with weighted loss
- Deployed on Hugging Face Hub: `BienKieu/mental-health`

### Training Process
```python
# See details in mental-health.ipynb
- Text preprocessing and cleaning
- Tokenization with BERT tokenizer
- Training with custom loss function
- Evaluation and visualization
- Push model to Hugging Face Hub
```

### Fine-tuning on Imbalanced Data (7 labels)

- Problem: Class imbalance across 7 labels: `Anxiety`, `Bipolar`, `Depression`, `Normal`, `Personality disorder`, `Stress`, `Suicidal`.
- Technique: Weighted Cross-Entropy Loss to penalize minority classes more heavily.
- Split: Train/Test = 80/20.
- Backbone: `bert-base-uncased`, fine-tuned with class weights computed from label frequencies.
- Training notebook (Kaggle): `https://www.kaggle.com/code/battboii/mental-health`

### Result (Test 20%)

Evaluation results on the test set (confusion matrix / precision-recall-f1 per class):

```
                      precision    recall  f1-score   support

             Anxiety       0.84      0.88      0.86       768
             Bipolar       0.85      0.85      0.85       556
          Depression       0.76      0.73      0.75      3081
              Normal       0.94      0.93      0.93      3264
Personality disorder       0.77      0.75      0.76       215
              Stress       0.72      0.72      0.72       517
            Suicidal       0.68      0.71      0.70      2131

            accuracy                           0.81     10532
           macro avg       0.79      0.80      0.80     10532
        weighted avg       0.81      0.81      0.81     10532
```

## Installation and Setup

### System Requirements
- Python 3.11+
- Node.js (for frontend)
- GPU (recommended for model training)

### 1. Clone repository
```bash
git clone https://github.com/BienKieu1411/CalmMind
cd CalmMind
```

### 2. Install Backend
```bash
pip install -r requirements.txt
```

### 3. Install Frontend
```bash
cd client
# Open index.html in browser
# Or use live server
python -m http.server 7860
```

### 4. Run Backend Server
```bash
cd api
python run.py
# Server will run on http://localhost:7860
```

### 5. Access Application
Open browser and navigate to: `http://localhost:7860` (or index.html file)

## Configuration

### Environment Variables
Create `.env` file in `server/` directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### Required API Keys
1. **Groq API**: For generating personalized suggestions
2. **Hugging Face Token**: For accessing ML model

## API Endpoints

### POST `/analyze`
Analyze text and return classification + suggestions

**Request:**
```json
{
  "text": "I feel very stressed and anxious about work"
}
```

**Response:**
```json
{
  "translated_text": "I feel very stressed and anxious about work",
  "classification": "anxiety",
  "suggestions": "1. Practice deep breathing exercises...",
  "user_language": "en"
}
```

## Key Features

### 1. Automatic Language Detection
- Uses `langdetect` library
- Multi-language support
- Automatic translation to English for processing

### 2. Mental Health Classification
- 7 categories: anxiety, bipolar, depression, normal, personality disorder, stress, suicidal
- High accuracy with BERT model
- Real-time processing via Gradio client

### 3. Personalized Suggestions
- Uses Groq LLM (GPT-oss-20b)
- Practical and actionable suggestions
- Customized to user's language

### 4. User Interface
- Responsive design
- Loading states and error handling
- Visual results display with icons

## Security and Privacy

- No user data storage
- Real-time processing, no persistence
- CORS configured for development
- API keys protected via environment variables

## Development

### Code Structure
```
client/
├── index.html      # Main HTML structure
├── styles.css      # Styling and responsive design
└── script.js       # Frontend logic and API calls

api/
├── app.py         # FastAPI application
└── run.py         # Server runner

mental-health.ipynb # ML model training notebook

requirements.txt # Python dependencies

vercel.json # Set up vercel 
```

### Adding New Features
1. **Frontend**: Edit `client/script.js` and `client/styles.css`
2. **Backend**: Add endpoints in `api/app.py`
3. **ML Model**: Update notebook and retrain model

## Performance

- **Backend**: FastAPI with async/await
- **ML Inference**: Gradio client with caching
- **Translation**: LibreTranslate API with timeout
- **LLM**: Groq API with optimized parameters

## Troubleshooting

### Common Issues

1. **"Backend server is not running"**
   - Check if server is running on port 8000
   - View logs in terminal

2. **"Analysis failed"**
   - Check API keys in .env file
   - View network tab in DevTools

3. **Model not loading**
   - Check internet connection
   - Verify Hugging Face token

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push and create Pull Request

## License

MIT License - see LICENSE file for details

## Authors

- **Bien Kieu** - Developer & ML Engineer

## Acknowledgments

- Hugging Face for BERT model and hosting
- Groq for LLM API
- LibreTranslate for translation services
- FastAPI team for web framework
- Mental health dataset contributors

---

**Disclaimer**: CalmMind is for reference purposes only and does not replace professional medical advice. If you are experiencing a serious mental health crisis, please seek help from medical professionals.
