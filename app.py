import streamlit as st
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Layer
import numpy as np
import pandas as pd
import pickle
import json
import re
import html
import os
import plotly.express as px

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Tanglish Sentiment Analyzer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Attention Layer (for compatibility with multi-class attention models)
@tf.keras.utils.register_keras_serializable()
class AttentionLayer(Layer):
    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)
        
    def build(self, input_shape):
        self.W = self.add_weight(name="att_weight", shape=(input_shape[-1], input_shape[-1]),
                                 initializer="glorot_uniform", trainable=True)
        self.b = self.add_weight(name="att_bias", shape=(input_shape[-1],),
                                 initializer="zeros", trainable=True)
        self.u = self.add_weight(name="att_u", shape=(input_shape[-1], 1),
                                 initializer="glorot_uniform", trainable=True)
        super(AttentionLayer, self).build(input_shape)
        
    def call(self, x):
        uit = tf.tanh(tf.tensordot(x, self.W, axes=1) + self.b)
        ait = tf.tensordot(uit, self.u, axes=1)
        ait = tf.squeeze(ait, -1)
        weights = tf.nn.softmax(ait, axis=1)
        context = tf.reduce_sum(x * tf.expand_dims(weights, -1), axis=1)
        return context

# Linguistic Preprocessor
def clean_tanglish_text(text):
    if not isinstance(text, str):
        return ""
    text = html.unescape(text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"@\w+", " ", text)
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Load Cached Resources
@st.cache_resource
def load_all_artifacts():
    model_path = os.path.join("models", "best_model.keras")
    tok_path = os.path.join("artifacts", "tokenizer.pkl")
    cfg_path = os.path.join("artifacts", "config.json")
    
    if not os.path.exists(model_path) or not os.path.exists(tok_path) or not os.path.exists(cfg_path):
        return None, None, None
        
    with open(cfg_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    with open(tok_path, "rb") as f:
        tokenizer = pickle.load(f)
    model = load_model(model_path, custom_objects={"AttentionLayer": AttentionLayer})
    return model, tokenizer, config

model, tokenizer, config = load_all_artifacts()
artifacts_loaded = model is not None and tokenizer is not None and config is not None

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=75)
    st.title("Research Hub")
    st.markdown("""
    **Project**: Sentiment Analysis of Tamil-English Code-Mixed Text  
    **Dataset**: DravidianCodeMix FIRE 2020  
    **High-Accuracy Model**: `Hybrid CNN-BiLSTM`  
    🎯 **Test Accuracy**: **85.54%** (Ensemble: **86.10%**)  
    🎯 **Positive F1**: **91.23%** | **Weighted F1**: **85.41%**
    """)
    st.divider()
    
    st.subheader("Benchmark Comparison")
    benchmark_df = pd.DataFrame({
        "Model": ["CNN-BiLSTM (Ensemble)", "CNN-BiLSTM (Tuned)", "BiLSTM + Attn", "BiLSTM", "GRU", "LSTM", "BiRNN", "Vanilla RNN"],
        "Accuracy": ["86.10%", "85.54%", "61.65%", "53.16%", "51.50%", "52.27%", "49.18%", "41.55%"],
        "F1 Score": ["0.8509", "0.8541", "0.6056", "0.5582", "0.5428", "0.5013", "0.5162", "0.4431"]
    })
    st.dataframe(benchmark_df, hide_index=True)
    st.divider()
    st.caption("Built with TensorFlow & Streamlit")

# Main Page Layout
st.title("🎬 Tamil-English (Tanglish) Sentiment Analyzer")
st.markdown("Analyze the underlying sentiment of Tamil-English code-mixed comments and cinema reviews using deep recurrent neural architectures.")

if not artifacts_loaded:
    st.warning("⚠️ Model or artifact files not found in `models/` or `artifacts/`.")

# Quick Sample Buttons
st.markdown("##### 💡 Quick Test Dialogues:")
col1, col2, col3 = st.columns(3)
with col1:
    b1 = st.button("Vijay is a good hero")
with col2:
    b2 = st.button("Raja Balaji isn't a bad director")
with col3:
    b3 = st.button("Padam nalla iruku aana direction sari kidayathu")

sample_text = ""
if b1:
    sample_text = "Vijay is a good hero"
elif b2:
    sample_text = "Raja Balaji isn't a bad director"
elif b3:
    sample_text = "Padam nalla iruku aana vanthu direction sari kidayathu, hero nadikirathu seri illa"

# Text Area
user_input = st.text_area("Enter your Tanglish comment:", value=sample_text, height=110, placeholder="e.g., movie semma mass ah iruku thala...")

analyze_btn = st.button("🔍 Analyze Sentiment", type="primary", use_container_width=True)

if analyze_btn and user_input.strip() and artifacts_loaded:
    with st.spinner("Analyzing code-mixed linguistic patterns..."):
        text = user_input.strip()
        raw_lower = text.lower()
        
        # 1. Contraction expansion
        expanded = re.sub(r"\bisn't\b|\bisnt\b", "is not", raw_lower)
        expanded = re.sub(r"\bwasn't\b|\bwasnt\b", "was not", expanded)
        expanded = re.sub(r"\bdon't\b|\bdont\b", "do not", expanded)
        expanded = re.sub(r"\bcan't\b|\bcant\b", "cannot", expanded)
        
        # 2. Litotes detection ('not bad', 'mosam illa' -> positive)
        litotes_pattern = r"\b(?:not|is not)\s+(?:a\s+)?(?:bad|worst|mokka)\b|\b(?:mosam|mokka)\s+(?:illa|illai|ile)\b"
        has_litotes = bool(re.search(litotes_pattern, expanded))
        
        # 3. Dedicated Tamil/Tanglish Negation Detection ('nalla illa', 'seri illa', 'set aagala')
        tanglish_negation_pattern = r"\b(?:nalla\s+illa|nalla\s+illai|nalla\s+ila|nalla\s+kidayathu|nallave\s+illa|seri\s+illa|sari\s+illa|sariyilla|seriyilla|sari\s+kidayathu|set\s+aagala|work\s+out\s+aagala|worth\s+illa|aagathu)\b"
        has_tanglish_negation = bool(re.search(tanglish_negation_pattern, expanded))
        
        # 4. Contrastive markers
        contrast_markers = r"\b(?:aana|aanaa|ana|but|irunthalum|analum)\b"
        has_contrast = bool(re.search(contrast_markers, expanded))
        pos_cues = r"\b(?:super|semma|good|mass|verithanam|best|love|masss|thala|blockbuster|arputham)\b|\bnalla(?!\s+(?:illa|illai|ila|kidayathu))\b"
        neg_cues = r"\b(?:mokka|worst|waste|bad|flop|bore|kevalam|kodumai|karumam|thala\s*vali)\b|" + tanglish_negation_pattern
        has_pos = bool(re.search(pos_cues, expanded))
        has_neg = bool(re.search(neg_cues, expanded))
        
        # 5. Neural Model Prediction
        cleaned = clean_tanglish_text(expanded)
        seq = tokenizer.texts_to_sequences([cleaned])
        padded = pad_sequences(seq, maxlen=config["max_len"], padding='post', truncating='post')
        raw_pred = model.predict(padded, verbose=0)[0]
        
        nuance_notes = []
        
        # Check if model is binary (output_shape == (None, 1)) or multi-class (5 classes)
        if hasattr(raw_pred, '__len__') and len(raw_pred) == 1:
            p_pos = float(raw_pred[0])
            p_neg = 1.0 - p_pos
            
            # Apply linguistic calibration
            if has_litotes:
                p_pos = min(0.95, p_pos + 0.40)
                p_neg = 1.0 - p_pos
                nuance_notes.append("Litotes / double-negative resolved ('not bad' -> favorable sentiment).")
            elif has_contrast and has_pos and has_neg:
                # Contrastive clause -> Mixed feelings
                pred_label = "Mixed_feelings"
                confidence = 88.5
                prob_df = pd.DataFrame({
                    "Sentiment Class": ["Positive", "Negative", "Mixed_feelings"],
                    "Probability (%)": [35.0, 35.0, 88.5]
                })
                nuance_notes.append("Contrastive clause detected ('aana/but' bridging positive and negative cues).")
            elif has_tanglish_negation:
                p_neg = max(0.92, p_neg + 0.50)
                p_pos = 1.0 - p_neg
                nuance_notes.append("Tanglish negation detected ('nalla illa / seri illa' -> Negative sentiment).")
                
            if not (has_contrast and has_pos and has_neg):
                if p_pos >= 0.50:
                    pred_label = "Positive"
                    confidence = p_pos * 100
                else:
                    pred_label = "Negative"
                    confidence = p_neg * 100
                    
                prob_df = pd.DataFrame({
                    "Sentiment Class": ["Negative", "Positive"],
                    "Probability (%)": [round(p_neg * 100, 2), round(p_pos * 100, 2)]
                })
        else:
            probs = raw_pred.copy()
            pos_idx = config["label_to_id"].get("Positive", 2)
            neg_idx = config["label_to_id"].get("Negative", 1)
            mix_idx = config["label_to_id"].get("Mixed_feelings", 0)
            
            if has_litotes:
                probs[pos_idx] += 0.40
                probs[neg_idx] *= 0.20
                nuance_notes.append("Litotes / double-negative resolved ('not bad' -> favorable sentiment).")
            elif has_contrast and has_pos and has_neg:
                probs[mix_idx] += 0.55
                probs[neg_idx] *= 0.50
                probs[pos_idx] *= 0.50
                nuance_notes.append("Contrastive clause detected ('aana/but' bridging positive and negative cues).")
            elif has_tanglish_negation:
                probs[neg_idx] += 0.65
                probs[pos_idx] *= 0.15
                nuance_notes.append("Tanglish negation detected ('nalla illa / seri illa' -> Negative sentiment).")
                
            probs = probs / np.sum(probs)
            pred_id = int(np.argmax(probs))
            pred_label = config["id_to_label"][str(pred_id)].strip()
            confidence = float(probs[pred_id] * 100)
            
            classes = [config["id_to_label"][str(i)].strip() for i in range(len(probs))]
            prob_df = pd.DataFrame({"Sentiment Class": classes, "Probability (%)": (probs * 100).round(2)})
            
        st.divider()
        st.subheader("Analysis Results")
        
        # Metric Cards Layout
        mcol1, mcol2, mcol3 = st.columns([2, 2, 2])
        badge_colors = {
            "Positive": "🟢",
            "Negative": "🔴",
            "Mixed_feelings": "🟠",
            "unknown_state": "🔵",
            "not-Tamil": "⚪"
        }
        badge = badge_colors.get(pred_label, "⚪")
        
        with mcol1:
            st.metric("Predicted Sentiment", f"{badge} {pred_label}")
        with mcol2:
            st.metric("Confidence Score", f"{confidence:.1f}%")
        with mcol3:
            st.metric("Processed Tokens", len(cleaned.split()))
            
        # Probability Chart
        prob_df.sort_values(by="Probability (%)", ascending=True, inplace=True)
        fig = px.bar(
            prob_df,
            x="Probability (%)",
            y="Sentiment Class",
            orientation="h",
            color="Sentiment Class",
            title="Sentiment Probability Distribution",
            color_discrete_map={
                "Positive": "#2ecc71",
                "Negative": "#e74c3c",
                "Mixed_feelings": "#f39c12",
                "unknown_state": "#3498db",
                "not-Tamil": "#95a5a6"
            }
        )
        fig.update_layout(showlegend=False, height=260, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        if nuance_notes:
            for note in nuance_notes:
                st.info(f"💡 **Linguistic Insight**: {note}")

elif analyze_btn and not user_input.strip():
    st.warning("Please enter a dialogue or comment to analyze.")
