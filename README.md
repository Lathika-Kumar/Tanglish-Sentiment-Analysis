# 🎬 Tanglish Sentiment Analyzer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.13-blue.svg)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15%2B-orange.svg)](https://tensorflow.org/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/Lathika-Kumar/Tanglish-Sentiment-Analysis)

An end-to-end research and production framework for **Sentiment Analysis of Tamil-English (Tanglish) Code-Mixed Social Comments** using deep recurrent neural networks (Vanilla RNN, BiRNN, LSTM, GRU, BiLSTM, Seq2Seq, BiLSTM + Attention, and Hybrid CNN-BiLSTM).

---

## 📌 Project Highlights

- **Official Dataset**: Evaluated on **DravidianCodeMix-FIRE 2020** ($43,991$ real YouTube movie comments).
- **High-Accuracy Polarity Benchmark**: Achieves **85.54% – 86.10% Test Accuracy** with **91.23% Positive F1 Score**.
- **Comprehensive Model Benchmark**: Rigorously compares 7 distinct recurrent and hybrid neural architectures under strictly controlled experimental setups.
- **Linguistic Preprocessing & Calibration**:
  - Unescapes HTML entities, handles repeated character elongations (`semmaaaa` $\to$ `semma`).
  - Resolves **Tanglish Negation Bigrams** (`nalla illa`, `seri illa`, `set aagala` $\to$ Negative).
  - Handles **Litotes / Double Negatives** (`isn't bad`, `not a bad director` $\to$ Positive).
  - Detects **Contrastive Discourse** (`aana`, `but`, `irundhalum` bridging positive and negative cues $\to$ `Mixed_feelings`).
- **Interactive Web App**: Built with **Streamlit** featuring real-time inference, dynamic confidence meters, linguistic insight cards, and Plotly horizontal probability charts.

---

## 🏆 Experimental Benchmark Results

### 1. High-Accuracy Polarity Benchmark (Positive vs. Negative)

| Model Architecture | Test Accuracy | Macro F1 | Positive F1 | Weighted F1 | Train Time |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 🥇 **Ensemble Fusion (Soft-Voting)** | **86.10%** | **0.7310** | **0.9180** | **0.8509** | — |
| 🥈 **Hybrid CNN-BiLSTM (Tuned)** | **85.54%** | **0.7499** | **0.9123** | **0.8541** | 36.4 s |

### 2. Comprehensive 5-Class Recurrent Comparative Benchmark

Evaluated on the full 5-class DravidianCodeMix test partition ($4,402$ held-out comments):

| Model Architecture | Test Accuracy | Macro F1 | Weighted F1 | Macro Precision | Macro Recall | Train Time |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **BiLSTM + Attention (Champion)** | **61.65%** | **0.4798** | **0.6056** | **0.4898** | **0.5069** | 55.1 s |
| **BiLSTM** | 53.16% | 0.4689 | 0.5582 | 0.4484 | 0.5404 | 42.8 s |
| **GRU** | 51.50% | 0.4517 | 0.5428 | 0.4352 | 0.5166 | 37.5 s |
| **LSTM** | 52.27% | 0.3693 | 0.5013 | 0.3839 | 0.4199 | 50.1 s |
| **Seq2Seq** | 51.43% | 0.3790 | 0.5100 | 0.3937 | 0.4241 | 45.3 s |
| **BiRNN** | 49.18% | 0.4182 | 0.5162 | 0.4089 | 0.5198 | 31.0 s |
| **Vanilla RNN** | 41.55% | 0.3262 | 0.4431 | 0.3194 | 0.3749 | 32.8 s |

---

## 📂 Project Directory Structure

```text
Tanglish-Sentiment-Analysis/
│
├── app.py                     # Interactive Streamlit Web Application
├── requirements.txt           # Python library dependencies
├── README.md                  # Project overview & experimental benchmarks
├── run_app.bat                # 1-Click Windows Application Launcher
│
├── models/
│   └── best_model.keras       # Trained High-Accuracy Neural Model (~40 MB)
│
├── artifacts/
│   ├── tokenizer.pkl          # Pickled Keras Tokenizer (25,000 vocab)
│   ├── label_encoder.pkl      # Pickled Scikit-Learn LabelEncoder
│   ├── config.json            # Model parameters & experimental metrics
│   ├── label_mapping.json     # Bidirectional class mapping dictionary
│   └── comprehensive_evaluation_metrics.csv
│
└── notebooks/
    └── sentiment_analysis.ipynb
```

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/Lathika-Kumar/Tanglish-Sentiment-Analysis.git
cd Tanglish-Sentiment-Analysis
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
- **Windows (1-Click)**: Double-click `run_app.bat`.
- **Command Line**:
  ```bash
  streamlit run app.py
  ```
- Open your browser at: **`http://localhost:8501`**

---

## 🧪 Sample Dialogue Evaluations

| Input Dialogue / Comment | Predicted Sentiment | Key Linguistic Insight |
| :--- | :---: | :--- |
| `"Vijay is a good hero"` | **Positive** 🟢 | Clear unigram polarity detection |
| `"movie semma super ah iruku"` | **Positive** 🟢 | Intense code-mixed colloquial praise (96.2% confidence) |
| `"padam nalla illa"` | **Negative** 🔴 | Post-positional Tanglish negation coupling resolved |
| `"Raja Balaji isn't a bad director"` | **Positive** 🟢 | Litotes / double-negative resolution |
| `"Padam nalla iruku aana direction sari kidayathu"` | **Mixed_feelings** 🟠 | Contrastive discourse marker (`aana`) bridging polarities |

---

## 📜 Citation & Benchmark Attribution
This implementation utilizes data from:
> **Chakravarthi, B. R., et al. (2020)**. *Overview of the Track on Sentiment Analysis for Dravidian Languages in Code-Mixed Text.* In Forum for Information Retrieval Evaluation (FIRE 2020).
