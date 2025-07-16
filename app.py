# app.py - Streamlit NLP AI Assistant with Banner & Footer

import streamlit as st
from transformers import pipeline
import time

# ----------------------
# Page Configuration
# ----------------------
st.set_page_config(page_title="NLP AI Assistant", layout="centered", page_icon="🤖")

# ----------------------
# Custom CSS for Styling
# ----------------------
st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 2.6em;
        color: #3a86ff;
        font-weight: bold;
    }
    .footer {
        text-align: center;
        color: grey;
        font-size: 0.9em;
        margin-top: 40px;
    }
    .loader {
        font-size: 1.2em;
        font-weight: bold;
        color: #ff006e;
        text-align: center;
        animation: move 1.5s infinite;
    }
    @keyframes move {
        0% { opacity: 0.2; }
        50% { opacity: 1; }
        100% { opacity: 0.2; }
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------
# Load Models
# ----------------------
sentiment_pipe = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
ner_pipe = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

# 🌍 Supported Languages
languages = {
    "Hindi": "Helsinki-NLP/opus-mt-en-hi",
    "Tamil": "Helsinki-NLP/opus-mt-en-ta",
    "French": "Helsinki-NLP/opus-mt-en-fr",
    "German": "Helsinki-NLP/opus-mt-en-de",
    "Spanish": "Helsinki-NLP/opus-mt-en-es",
    "Italian": "Helsinki-NLP/opus-mt-en-it",
    "Russian": "Helsinki-NLP/opus-mt-en-ru",
    "Bengali": "Helsinki-NLP/opus-mt-en-bn",
    "Gujarati": "Helsinki-NLP/opus-mt-en-gu",
    "Telugu": "Helsinki-NLP/opus-mt-en-te",
    "Marathi": "Helsinki-NLP/opus-mt-en-mr",
    "Urdu": "Helsinki-NLP/opus-mt-en-ur",
    "Arabic": "Helsinki-NLP/opus-mt-en-ar",
    "Chinese": "Helsinki-NLP/opus-mt-en-zh",
    "Japanese": "Helsinki-NLP/opus-mt-en-jap",
    "Kannada": "Helsinki-NLP/opus-mt-en-kn",
    "Malayalam": "Helsinki-NLP/opus-mt-en-ml",
    "Punjabi": "Helsinki-NLP/opus-mt-en-pa",
    "Nepali": "Helsinki-NLP/opus-mt-en-ne",
    "Korean": "Helsinki-NLP/opus-mt-en-ko",
    "Dutch": "Helsinki-NLP/opus-mt-en-nl",
    "Romanian": "Helsinki-NLP/opus-mt-en-ro",
    "Swedish": "Helsinki-NLP/opus-mt-en-sv",
    "Portuguese": "Helsinki-NLP/opus-mt-en-pt",
    "Thai": "Helsinki-NLP/opus-mt-en-th"
}

# ----------------------
# App UI
# ----------------------
st.markdown('<div class="title">🤖 Mini NLP AI Assistant</div>', unsafe_allow_html=True)
st.markdown("### ✍️ Enter an English sentence below:")

sentence = st.text_input("Your Sentence", placeholder="Type something meaningful...")

lang = st.selectbox("🌐 Choose a language for translation", list(languages.keys()))

# Process Button
if sentence:
    with st.spinner("Processing... Please wait..."):
        st.markdown('<div class="loader">🚀 Performing Sentiment, NER, and Translation...</div>', unsafe_allow_html=True)
        time.sleep(1.5)

        # Load translator dynamically
        translator = pipeline("translation", model=languages[lang])
        sentiment = sentiment_pipe(sentence)[0]
        ner = ner_pipe(sentence)
        translated = translator(sentence)[0]['translation_text']

    # ----------------------
    # Display Results
    # ----------------------
    st.success("✅ All tasks completed!")

    st.markdown("## 🔍 Sentiment Analysis")
    st.write(f"**Sentiment:** `{sentiment['label']}` | **Confidence:** `{round(sentiment['score'] * 100, 2)}%`")

    st.markdown("## 🏷️ Named Entity Recognition")
    if ner:
        for ent in ner:
            st.write(f"**{ent['word']}** → `{ent['entity_group']}`")
    else:
        st.info("No named entities found.")

    st.markdown(f"## 🌐 Translated to {lang}")
    st.text_area("Translation", translated, height=100)

    # ----------------------
    # Footer
    # ----------------------
    st.markdown('<div class="footer">👨‍💻 <b>Team 2</b>: Sakthivel, Hemanth, Ananth alias Kannamma, Harishmani, Lognath<br>✨ Powered by HuggingFace Transformers & Developed with ❤️ in Streamlit</div>', unsafe_allow_html=True)
