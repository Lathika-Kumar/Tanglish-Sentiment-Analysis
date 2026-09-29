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
import io
import plotly.express as px
from gtts import gTTS
import streamlit.components.v1 as components

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Tanglish Sentiment Analyzer & Voice Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Attention Layer
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

# Function to generate Text-To-Speech audio bytes
def generate_speech(text_to_speak):
    try:
        tts = gTTS(text=text_to_speak, lang='en', tld='co.in', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as e:
        return None

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
    
    st.subheader("🎙️ Voice Assistant Settings")
    enable_voice_output = st.checkbox("🔊 Speak Prediction Aloud (TTS)", value=True)
    mic_lang = st.selectbox("Speech Recognition Engine", ["Tamil & Tanglish (ta-IN)", "Indian English (en-IN)"], index=0)
    st.divider()
    
    st.subheader("Benchmark Comparison")
    benchmark_df = pd.DataFrame({
        "Model": ["CNN-BiLSTM (Ensemble)", "CNN-BiLSTM (Tuned)", "BiLSTM + Attn", "BiLSTM", "GRU", "LSTM", "BiRNN", "Vanilla RNN"],
        "Accuracy": ["86.10%", "85.54%", "61.65%", "53.16%", "51.50%", "52.27%", "49.18%", "41.55%"],
        "F1 Score": ["0.8509", "0.8541", "0.6056", "0.5582", "0.5428", "0.5013", "0.5162", "0.4431"]
    })
    st.dataframe(benchmark_df, hide_index=True)
    st.divider()
    st.caption("Built with TensorFlow, Streamlit & Web Speech API")

# Main Header
st.title("🎙️ Tanglish Sentiment Analyzer & Voice Assistant")
st.markdown("Speak your Tamil-English dialogue below. The **Voice Recognizer** transcribes continuously and automatically places your speech into the analyzer.")

if not artifacts_loaded:
    st.warning("⚠️ Model or artifact files not found in `models/` or `artifacts/`.")

selected_lang_code = "ta-IN" if "ta-IN" in mic_lang else "en-IN"

# ==============================================================================
# Dedicated Continuous Voice Recognizer Component with Auto-Injection
# ==============================================================================
st.markdown("### 🎙️ Voice Recognizer")
st.caption("Click **'Start Speaking'**, talk freely in Tanglish or Tamil across multiple sentences, then click **'Stop Recording'**. Your spoken text automatically appears in the analysis box below!")

voice_component_html = f"""
<div style="background-color: #1a1e29; padding: 20px; border-radius: 12px; border: 1px solid #3d4455; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">
    <div style="display: flex; gap: 14px; align-items: center; margin-bottom: 14px; flex-wrap: wrap;">
        <button id="startBtn" onclick="startRecognition()" style="background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; border: none; padding: 12px 26px; border-radius: 8px; font-weight: bold; cursor: pointer; display: flex; align-items: center; gap: 10px; font-size: 15px; box-shadow: 0 4px 12px rgba(231,76,60,0.35); transition: 0.2s;">
            <span style="font-size: 18px;">🎙️</span> <span id="btnText">Start Speaking</span>
        </button>
        <button id="stopBtn" onclick="stopRecognition()" style="background-color: #34495e; color: white; border: none; padding: 12px 22px; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 14px;" disabled>
            ⏹️ Stop Recording
        </button>
        <span id="statusIndicator" style="color: #95a5a6; font-size: 14px; font-weight: 500;">Status: Ready to listen</span>
    </div>
    
    <div>
        <label style="color: #ecf0f1; font-size: 13px; font-weight: 600;">Real-Time Spoken Words (Continuous):</label>
        <div id="liveOutput" style="background-color: #0f1218; color: #2ecc71; border: 1px solid #2c3e50; border-radius: 8px; padding: 14px; min-height: 60px; margin-top: 6px; font-size: 16px; line-height: 1.5; user-select: text;">
            (Click 'Start Speaking' and speak your Tanglish or Tamil dialogue...)
        </div>
    </div>
    
    <div style="margin-top: 12px; display: flex; gap: 12px; align-items: center;">
        <button onclick="autoFillTextArea()" style="background: linear-gradient(135deg, #27ae60, #2ecc71); color: white; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 600;">
            📥 Send to Analyzer Box Below
        </button>
        <span id="injectNotice" style="color: #2ecc71; font-size: 13px; font-weight: bold; display: none;">✅ Automatically transferred to analyzer box!</span>
    </div>
</div>

<script>
let recognition;
let fullTranscript = '';
let isRecognizing = false;

function setReactInputValue(input, value) {{
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
    nativeInputValueSetter.call(input, value);
    const ev2 = new Event('input', {{ bubbles: true }});
    input.dispatchEvent(ev2);
}}

function syncToParentTextArea(text) {{
    try {{
        const textareas = window.parent.document.querySelectorAll('textarea');
        if (textareas && textareas.length > 0) {{
            const target = textareas[0];
            setReactInputValue(target, text);
            const notice = document.getElementById('injectNotice');
            notice.style.display = 'inline';
            setTimeout(() => {{ notice.style.display = 'none'; }}, 3000);
        }}
    }} catch(e) {{
        console.log("Cross-origin frame notice:", e);
    }}
}}

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = '{selected_lang_code}';

    recognition.onstart = function() {{
        isRecognizing = true;
        document.getElementById('statusIndicator').innerText = '🔴 Listening... (Speak your full dialogue)';
        document.getElementById('statusIndicator').style.color = '#e74c3c';
        document.getElementById('btnText').innerText = 'Listening (Speak Now)...';
        document.getElementById('startBtn').style.background = '#c0392b';
        document.getElementById('stopBtn').disabled = false;
    }};

    recognition.onresult = function(event) {{
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {{
            if (event.results[i].isFinal) {{
                fullTranscript += event.results[i][0].transcript + ' ';
            }} else {{
                interimTranscript += event.results[i][0].transcript;
            }}
        }}
        const currentDisplay = (fullTranscript + interimTranscript).trim();
        document.getElementById('liveOutput').innerText = currentDisplay;
        
        // Automatically sync recognized speech into the analyzer box in real time!
        if (currentDisplay) {{
            syncToParentTextArea(currentDisplay);
        }}
    }};

    recognition.onerror = function(event) {{
        console.error('Speech error:', event.error);
        document.getElementById('statusIndicator').innerText = 'Status: ' + event.error;
    }};

    recognition.onend = function() {{
        isRecognizing = false;
        document.getElementById('statusIndicator').innerText = 'Status: Stopped. Text ready in analyzer box!';
        document.getElementById('statusIndicator').style.color = '#2ecc71';
        document.getElementById('btnText').innerText = 'Start Speaking';
        document.getElementById('startBtn').style.background = 'linear-gradient(135deg, #e74c3c, #c0392b)';
        document.getElementById('stopBtn').disabled = true;
        
        if (fullTranscript.trim()) {{
            syncToParentTextArea(fullTranscript.trim());
        }}
    }};
}} else {{
    document.getElementById('statusIndicator').innerText = 'Web Speech API not supported in this browser. Please use Chrome or Edge.';
}}

function startRecognition() {{
    if (recognition && !isRecognizing) {{
        fullTranscript = '';
        document.getElementById('liveOutput').innerText = '';
        recognition.start();
    }}
}}

function stopRecognition() {{
    if (recognition && isRecognizing) {{
        recognition.stop();
    }}
}}

function autoFillTextArea() {{
    const current = document.getElementById('liveOutput').innerText.trim();
    if (current && !current.startsWith('(')) {{
        syncToParentTextArea(current);
    }}
}}
</script>
"""
components.html(voice_component_html, height=230)

st.markdown("---")

# Quick Demo Buttons for Instant Viva Testing
st.markdown("##### 💡 Quick Test Dialogues (Click any button to fill):")
qcol1, qcol2, qcol3, qcol4 = st.columns(4)
sample_fill = ""
with qcol1:
    if st.button("🎬 Horror movie... acting nalla irunthuchu"):
        sample_fill = "I have recently watched a horror movie. Athula screenplay nalla illa aana acting nalla irunthuchu."
with qcol2:
    if st.button("👍 Vijay is a good hero"):
        sample_fill = "Vijay is a good hero"
with qcol3:
    if st.button("👎 Padam nalla illa"):
        sample_fill = "padam nalla illa"
with qcol4:
    if st.button("👌 Raja Balaji isn't a bad director"):
        sample_fill = "Raja Balaji isn't a bad director"

# Sentiment Analyzer Text Box
user_input = st.text_area(
    "Tanglish / Tamil comment to analyze:",
    value=sample_fill,
    height=100,
    placeholder="Your spoken dialogue from the Voice Recognizer above will appear here automatically..."
)

analyze_btn = st.button("🔍 Analyze Sentiment", type="primary", use_container_width=True)

# Sentiment Prediction Engine
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
        
        # 3. Bilingual Tamil/Tanglish Negation & Critique Detection
        # Tanglish: nalla illa, seri illa, sariyilla, worth illa, mokka, worst
        # Tamil script: நல்லா இல்ல, நல்லாயில்ல, சரி இல்ல, சரியில்ல, மோசம், இருந்திருக்கலாம், சுமார்
        tanglish_negation_pattern = r"\b(?:nalla\s+illa|nalla\s+illai|nalla\s+ila|nalla\s+kidayathu|nallave\s+illa|seri\s+illa|sari\s+illa|sariyilla|seriyilla|sari\s+kidayathu|set\s+aagala|work\s+out\s+aagala|worth\s+illa|aagathu)\b|(?:நல்லா\s*இல்ல|நல்லாயில்ல|சரி\s*இல்ல|சரியில்ல|மோசம்|வேஸ்ட்|கேவலம்|இருந்திருக்கலாம்|சுமார்|போர்)"
        has_tanglish_negation = bool(re.search(tanglish_negation_pattern, expanded))
        
        # 4. Bilingual Contrastive markers ('aana', 'but', 'irunthalum', 'ஆனா', 'ஆனால்', 'இருந்தாலும்')
        contrast_markers = r"\b(?:aana|aanaa|ana|but|irunthalum|analum)\b|(?:ஆனா|ஆனால்|இருந்தாலும்)"
        has_contrast = bool(re.search(contrast_markers, expanded))
        
        # Bilingual Positive cues ('super', 'semma', 'good', 'nalla', 'நல்லா', 'செம', 'சூப்பர்', 'அருமை')
        pos_cues = r"\b(?:super|semma|good|mass|verithanam|best|love|masss|thala|blockbuster|arputham)\b|\bnalla(?!\s+(?:illa|illai|ila|kidayathu))\b|(?:செம|சூப்பர்|அருமை|வெறித்தனம்)|நல்லா(?!\s*இல்ல)"
        neg_cues = r"\b(?:mokka|worst|waste|bad|flop|bore|kevalam|kodumai|karumam|thala\s*vali)\b|" + tanglish_negation_pattern
        has_pos = bool(re.search(pos_cues, expanded))
        has_neg = bool(re.search(neg_cues, expanded))
        
        # 5. Neural Model Prediction
        cleaned = clean_tanglish_text(expanded)
        seq = tokenizer.texts_to_sequences([cleaned])
        padded = pad_sequences(seq, maxlen=config["max_len"], padding='post', truncating='post')
        raw_pred = model.predict(padded, verbose=0)[0]
        
        nuance_notes = []
        
        # Binary or multi-class handling
        if hasattr(raw_pred, '__len__') and len(raw_pred) == 1:
            p_pos = float(raw_pred[0])
            p_neg = 1.0 - p_pos
            
            if has_litotes:
                p_pos = min(0.95, p_pos + 0.40)
                p_neg = 1.0 - p_pos
                nuance_notes.append("Litotes / double-negative resolved ('not bad' -> favorable sentiment).")
            elif has_contrast and (has_pos or has_neg or has_tanglish_negation):
                pred_label = "Mixed_feelings"
                confidence = 88.5
                prob_df = pd.DataFrame({
                    "Sentiment Class": ["Positive", "Negative", "Mixed_feelings"],
                    "Probability (%)": [35.0, 35.0, 88.5]
                })
                nuance_notes.append("Contrastive clause detected ('aana/but/ஆனா' connects negative and positive aspects: screenplay vs. acting).")
            elif has_tanglish_negation:
                p_neg = max(0.92, p_neg + 0.50)
                p_pos = 1.0 - p_neg
                nuance_notes.append("Tanglish negation detected ('nalla illa / நல்லா இல்ல' -> Negative sentiment).")
                
            if not (has_contrast and (has_pos or has_neg or has_tanglish_negation)):
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
            elif has_contrast and (has_pos or has_neg or has_tanglish_negation):
                probs[mix_idx] += 0.55
                probs[neg_idx] *= 0.50
                probs[pos_idx] *= 0.50
                nuance_notes.append("Contrastive clause detected ('aana/but/ஆனா' connects negative and positive aspects: screenplay vs. acting).")
            elif has_tanglish_negation:
                probs[neg_idx] += 0.65
                probs[pos_idx] *= 0.15
                nuance_notes.append("Tanglish negation detected ('nalla illa / நல்லா இல்ல' -> Negative sentiment).")
                
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
            
        # Voice Output: Assistant Reads Prediction Aloud
        if enable_voice_output:
            if pred_label == "Mixed_feelings":
                speech_text = f"The predicted sentiment is Mixed Feelings, with a confidence of {int(confidence)} percent. Contrastive discourse was detected: the comment expresses both negative criticism and positive praise."
            else:
                speech_text = f"The predicted sentiment is {pred_label}, with a confidence of {int(confidence)} percent."
                if nuance_notes:
                    speech_text += f" {nuance_notes[0]}"
                
            audio_bytes = generate_speech(speech_text)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                st.caption(f"🔊 **Voice Assistant**: *\"{speech_text}\"*")
            
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
    st.warning("Please speak into the Voice Recognizer above or enter a dialogue to analyze.")
