# app.py – Streamlit NLP AI Assistant with translation, NER, sentiment

import streamlit as st
from transformers import pipeline
import time

# Page Config
st.set_page_config(page_title="NLP AI Assistant", page_icon="🤖", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 2.6em;
        color: #3a86ff;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .footer {
        text-align: center;
        color: grey;
        font-size: 0.9em;
        margin-top: 50px;
    }
    .loader {
        font-size: 1.1em;
        font-weight: bold;
        color: #ff006e;
        text-align: center;
        animation: blink 1.2s infinite;
    }
    @keyframes blink {
        0% { opacity: 0.2; }
        50% { opacity: 1; }
        100% { opacity: 0.2; }
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="title">🤖 Mini NLP AI Assistant</div>', unsafe_allow_html=True)
st.write("Perform **Sentiment Analysis**, **Named Entity Recognition (NER)**, and **Translation** using 🤗 Hugging Face models.")

# Load models
sentiment_pipe = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
ner_pipe = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

# Translation languages
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

# User input
sentence = st.text_input("📝 Enter your English sentence:")
selected_lang = st.selectbox("🌍 Translate to:", list(languages.keys()))

# Trigger on sentence
if sentence:
    with st.spinner("Processing..."):
        st.markdown('<div class="loader">⏳ Analyzing input, translating, and recognizing entities...</div>', unsafe_allow_html=True)
        time.sleep(1.5)

        # Translation pipeline (dynamic load)
        translator = pipeline("translation", model=languages[selected_lang])

        # Inference
        sentiment = sentiment_pipe(sentence)[0]
        ner_result = ner_pipe(sentence)
        translation = translator(sentence)[0]['translation_text']

    # Display results
    st.success("✅ Done!")

    st.markdown("## 🔍 Sentiment Analysis")
    st.write(f"**Sentiment:** `{sentiment['label']}` | **Confidence:** `{round(sentiment['score']*100, 2)}%`")

    st.markdown("## 🏷️ Named Entities")
    if ner_result:
        for ent in ner_result:
            st.write(f"**{ent['word']}** → `{ent['entity_group']}`")
    else:
        st.info("No named entities found.")

    st.markdown(f"## 🌐 Translation to {selected_lang}")
    st.text_area("Translated Text", translation, height=100)

    # Footer
    st.markdown('<div class="footer">👨‍💻 <b>Team 2</b>: Sakthivel, Hemanth, Ananth alias Kannamma, Harishmani, Lognath<br>📦 Powered by HuggingFace Transformers & ❤️ Streamlit</div>', unsafe_allow_html=True)
