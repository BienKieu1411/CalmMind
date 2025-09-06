from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langdetect import detect
import httpx
from groq import Groq
import re
import os

load_dotenv()

app = FastAPI(title="CalmMind Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    translated_text: str | None = None
    classification: str
    suggestions: str
    user_language: str

_groq_client = None
_gradio_client = None

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        try:
            _groq_client = Groq()
        except Exception:
            pass
    return _groq_client

def get_gradio_client():
    global _gradio_client
    if _gradio_client is None:
        try:
            from gradio_client import Client
            _gradio_client = Client("BienKieu/mental-health")
        except Exception:
            pass
    return _gradio_client

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "en"

async def translate_to_english(text: str, from_language: str) -> str:
    if from_language == "en":
        return text
    try:
        async with httpx.AsyncClient(timeout=10) as client_http:
            response = await client_http.post(
                "https://libretranslate.de/translate",
                data={"q": text, "source": from_language, "target": "en", "format": "text"}
            )
        if response.status_code == 200:
            return response.json().get("translatedText", text)
        return text
    except Exception:
        return text

async def classify_mental_health(text: str) -> str:
    client = get_gradio_client()
    if client is None:
        return "unknown"
    try:
        result = client.predict(text, api_name="/_predict")
        if not result or not isinstance(result, (tuple, list)) or len(result) < 2:
            return "unknown"
        label = result[0]
        if not label or str(label).lower() in ["nan", ""]:
            return "unknown"
        return str(label)
    except Exception:
        return "unknown"

def format_suggestions(text: str) -> str:
    if not text.strip():
        return "No suggestions were generated."
    text = re.sub(r'^\s*[\d.o•\-\*]+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n\s*[\d.o•\-\*]+\s*', '<br><br>', text, flags=re.MULTILINE).strip()
    return "1. " + text.replace('\n', '<br>')

async def get_llm_suggestions(classification: str, user_language: str, original_text: str) -> str:
    client_groq = get_groq_client()
    if client_groq is None:
        return "Sorry, unable to generate suggestions at this time."

    suggestion_prompt = f"""You are a psychology expert. Provide 3-5 specific and actionable mental health suggestions for someone experiencing feelings related to the following text.

User's Text: "{original_text}"
Category: {classification}

Each suggestion should be short, practical, and easy to understand. Respond in {user_language} and format as a numbered list.
"""
    try:
        completion = client_groq.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": suggestion_prompt}],
            temperature=0.7,
            max_completion_tokens=600,
            top_p=0.9,
            reasoning_effort="medium",
            stream=False
        )
        raw_suggestions = completion.choices[0].message.content.strip()
        if not raw_suggestions or raw_suggestions.lower().startswith("sorry"):
            return "Sorry, unable to generate suggestions at this time."
        return format_suggestions(raw_suggestions)
    except Exception:
        return "Sorry, an error occurred while generating suggestions. Please try again later."

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_mental_health(user_input: UserInput):
    if not user_input.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    
    try:
        user_lang = detect_language(user_input.text)
        text_english = await translate_to_english(user_input.text, user_lang)
        classification = await classify_mental_health(text_english)
        suggestions = await get_llm_suggestions(classification, user_lang, user_input.text)
        
        return AnalysisResponse(
            translated_text=text_english if user_lang != 'en' else None,
            classification=classification,
            suggestions=suggestions,
            user_language=user_lang
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")