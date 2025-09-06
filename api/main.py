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

client_gradio = None
def get_gradio_client():
    global client_gradio
    if client_gradio is None:
        try:
            from gradio_client import Client
            client_gradio = Client("BienKieu/mental-health")
        except Exception as e:
            print("Error loading Gradio client:", e)
            client_gradio = None
    return client_gradio

class UserInput(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    translated_text: str | None = None
    classification: str
    suggestions: str
    user_language: str

def detect_language(text: str) -> str:
    lang = detect(text)
    print("Detected language:", lang)
    return lang

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
                translated = response.json().get("translatedText", text)
                print("Translated text:", translated)
                return translated
        return f"[{from_language.upper()}] {text}"
    except Exception as e:
        print("Translation error:", e)
        return f"[{from_language.upper()}] {text}"

async def classify_mental_health(text: str) -> str:
    client = get_gradio_client()
    if client is None:
        print("Gradio client not available")
        return "unknown"
    try:
        result = client.predict(text, api_name="/_predict")
        print("Raw Gradio predict result:", result)
        if isinstance(result, (tuple, list)):
            label = result[0]
        else:
            label = result
        label_str = str(label) if label else "unknown"
        print("Classification label:", label_str)
        return label_str
    except Exception as e:
        print("Classification error:", e)
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
        suggestion_prompt = f"""You are a psychology expert. Analyze the following text and provide practical mental health suggestions:

Category: {classification}
Text: "{translated_text}"

Provide 3-5 specific and useful mental health suggestions for this text. Each suggestion should:
- Be short and easy to understand
- Be practical and actionable
- Match the context described

Respond in {user_language} and format as follows:
1. First suggestion
2. Second suggestion
3. Third suggestion
..."""
        print("LLM suggestion prompt:", suggestion_prompt[:500], "...")  # in 500 ký tự đầu
        client_groq = Groq()
        completion = client_groq.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": suggestion_prompt}],
            temperature=0.7,
            max_completion_tokens=600,
            top_p=0.9,
            reasoning_effort="medium",
            stream=False
        )
        raw_suggestions = completion.choices[0].message.content.strip()
        print("Raw LLM suggestions:", raw_suggestions[:500], "...")
        if not raw_suggestions or raw_suggestions.lower().startswith("error"):
            return "Sorry, unable to generate suggestions at this time."
        formatted = format_suggestions(raw_suggestions)
        print("Formatted suggestions:", formatted[:500], "...")
        return formatted
    except Exception as e:
        print("LLM suggestion error:", e)
        return "Sorry, an error occurred while generating suggestions. Please try again later."

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_mental_health(user_input: UserInput):
    try:
        print("Input text:", user_input.text)
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
        print("Error in /analyze:", e)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
