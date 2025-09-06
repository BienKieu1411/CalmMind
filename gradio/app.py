import os
import re
import torch
import gradio as gr
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("omw-1.4")

stopwords_set = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"[^a-z\s]", " ", text)                   
    text = re.sub(r"\s+", " ", text).strip()
    
    words = text.split()
    filtered_words = [
        lemmatizer.lemmatize(w) for w in words if w not in stopwords_set and len(w) > 2
    ]
    return " ".join(filtered_words)

REPO_ID = os.environ.get("HF_MODEL_ID", "BienKieu/results")
MAX_LENGTH = int(os.environ.get("MAX_LENGTH", "512"))
torch.set_num_threads(int(os.environ.get("TORCH_NUM_THREADS", "1")))


tokenizer = AutoTokenizer.from_pretrained(REPO_ID)
model = AutoModelForSequenceClassification.from_pretrained(REPO_ID)

clf = pipeline(
    task="text-classification",
    model=model,
    tokenizer=tokenizer,
    device=-1,
    truncation=True,
    padding=True,   
    max_length=MAX_LENGTH   
)

id2label = model.config.id2label
labels = [id2label[i] for i in sorted(id2label.keys())]

def predict_one(text: str):
    if not text or not text.strip():
        return "", 0.0, {}

    text_clean = clean_text(text)

    results = clf(text_clean, truncation=True, max_length=MAX_LENGTH, return_all_scores=True)
    scores = results[0]
    scores_sorted = sorted(scores, key=lambda x: x["score"], reverse=True)
    pred = scores_sorted[0]
    pred_label, pred_score = pred["label"], float(pred["score"])
    score_map = {s["label"]: float(s["score"]) for s in scores_sorted}
    return pred_label, pred_score, score_map

with gr.Blocks(title="Mental Health Classifier") as demo:
    gr.Markdown("# Mental Health Classifier")

    inp = gr.Textbox(
        lines=3,
        placeholder="Input text...",
        label="Input"
    )
    btn = gr.Button("Predict")
    out_label = gr.Textbox(label="Predicted Label")
    out_score = gr.Number(label="Score", precision=6)
    out_table = gr.Dataframe(
        headers=["label", "score"],
        label="All label scores (sorted)",
        interactive=False
    )

    def _predict(text):
        pred_label, pred_score, score_map = predict_one(text)
        items = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
        table = pd.DataFrame(items, columns=["label", "score"])
        return pred_label, pred_score, table

    btn.click(
        _predict,
        inputs=[inp],
        outputs=[out_label, out_score, out_table]
    )

    gr.Markdown(f"**Model:** `{REPO_ID}`  •  **Max length:** {MAX_LENGTH}  •  **Labels:** {', '.join(labels)}")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))

"""
from gradio_client import Client
client = Client("BienKieu/mental-health")
result = client.predict(
    "I have been feeling very low and hopeless, nothing excites me anymore.", 
    api_name="/_predict"
)
label, score, _ = result
print("Predicted label:", label)
"""