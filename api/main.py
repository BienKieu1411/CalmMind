from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langdetect import detect
import httpx
from groq import Groq
import re
import time

load_dotenv()

app = FastAPI(title="CalmMind Backend", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client_gradio = None
MAX_RETRIES = 3

def load_gradio_client():
    global client_gradio
    retries = 0
    from gradio_client import Client as GradioClient
    while retries < MAX_RETRIES and client_gradio is None:
        try:
            client_gradio = GradioClient("BienKieu/mental-health")
            client_gradio.predict("Test")
        except Exception as e:
            print(f"Gradio client load failed ({retries+1}/{MAX_RETRIES}):", e)
            client_gradio = None
            retries += 1
            time.sleep(1)
    if client_gradio is None:
        print("Failed to load Gradio client after retries")

load_gradio_client()

class UserInput(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    translated_text: str | None = None
    classification: str
    suggestions: str
    user_language: str

def detect_language(text: str) -> str:
    return detect(text)

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
        return f"[{from_language.upper()}] {text}"
    except:
        return f"[{from_language.upper()}] {text}"

def clean_label(label: str) -> str:
    if not label:
        return "unknown"
    return re.sub(r"[*_`]", "", label).strip()

async def classify_mental_health(text: str) -> str:
    global client_gradio
    if client_gradio:
        try:
            result = client_gradio.predict(text, api_name="/_predict")
            label = result[0] if isinstance(result, (list, tuple)) else result
            return clean_label(str(label)) if label else "unknown"
        except Exception as e:
            print("Gradio classify error:", e)
    try:
        client_groq = Groq()
        prompt = f"Classify the following text into one of these categories: Normal, Anxiety, Depression, Stress, Suicidal, Bipolar, Personality disorder.\nText: \"{text}\""
        completion = client_groq.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            top_p=0.9,
            stream=False
        )
        raw_label = completion.choices[0].message.content.strip()
        if raw_label:
            return clean_label(raw_label.split("\n")[0])
    except Exception as e:
        print("LLM classify error:", e)
    return "unknown"

def format_suggestions(text: str) -> str:
    if not text.strip():
        return "No suggestions were generated."
    text = text.replace("**", "").replace("*", "").strip()
    patterns = [
        r"(?:\d+[\.\)]\s*)",
        r"(?:^|\n)(?=\d+[\.\)]\s)",
        r"(?:\n\s*)(?=\d+[\.\)]\s)",
        r"(?:^|\n)(?=[•\-\*]\s)",
        r"(?:\n\s*)(?=[•\-\*]\s)"
    ]
    suggestions = []
    for pattern in patterns:
        parts = re.split(pattern, text)
        if len(parts) > 1:
            suggestions = [part.strip() for part in parts if part.strip()]
            break
    if not suggestions:
        for sep in [r"\n\s*\n", r"\n(?=\d)", r"\n(?=[•\-\*])"]:
            parts = re.split(sep, text)
            if len(parts) > 1:
                suggestions = [part.strip() for part in parts if part.strip()]
                break
    if not suggestions:
        suggestions = [text]
    formatted_suggestions = []
    for i, suggestion in enumerate(suggestions):
        suggestion = re.sub(r"^(?:\d+[\.\)]\s*|[•\-\*]\s*)", "", suggestion).strip()
        if suggestion:
            suggestion = suggestion.replace('\n', '<br>')
            formatted_suggestions.append(f"{i+1}. {suggestion}")
    return "<br><br>".join(formatted_suggestions) if formatted_suggestions else "No suggestions were generated."

async def get_llm_suggestions(classification: str, user_language: str, original_text: str) -> str:
    try:
        text_language = detect_language(original_text)
        translated_text = await translate_to_english(original_text, text_language)
        prompt = f"""You are a psychology expert. Analyze the following text and provide practical mental health suggestions:

Category: {classification}
Text: "{translated_text}"

Provide 3-5 short, practical, actionable mental health suggestions.

Respond in {user_language} and format as:
1. First suggestion
2. Second suggestion
3. Third suggestion
..."""
        client_groq = Groq()
        completion = client_groq.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            top_p=0.9,
            stream=False
        )
        raw_suggestions = completion.choices[0].message.content.strip()
        return format_suggestions(raw_suggestions)
    except:
        return "Sorry, an error occurred while generating suggestions. Please try again later."

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_mental_health(user_input: UserInput):
    try:
        user_lang = detect_language(user_input.text)
        text_english = await translate_to_english(user_input.text, user_lang) if user_lang != 'en' else user_input.text
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