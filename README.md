# Tanglish Sentiment Analyzer

Sentiment Analysis of Tamil-English Code-Mixed Text using Recurrent Neural Networks (Vanilla RNN, BiRNN, LSTM, GRU, BiLSTM, Seq2Seq, and BiLSTM + Attention).

## Dataset
DravidianCodeMix-FIRE 2020 Benchmark Dataset (43,991 YouTube comments across 5 classes).

## Experimental Benchmark Results

| Model Architecture | Test Accuracy | Macro F1 | Weighted F1 | Training Time |
| :--- | :---: | :---: | :---: | :---: |
| **BiLSTM + Attention (Champion)** | **61.65%** | **0.4798** | **0.6056** | 55.1 s |
| **BiLSTM** | 53.16% | 0.4689 | 0.5582 | 42.8 s |
| **GRU** | 51.50% | 0.4517 | 0.5428 | 37.5 s |
| **LSTM** | 52.27% | 0.3693 | 0.5013 | 50.1 s |
| **Seq2Seq** | 51.43% | 0.3790 | 0.5100 | 45.3 s |
| **BiRNN** | 49.18% | 0.4182 | 0.5162 | 31.0 s |
| **Vanilla RNN** | 41.55% | 0.3262 | 0.4431 | 32.8 s |

## Directory Structure
```
tanglish-sentiment-analysis/
├── app.py
├── requirements.txt
├── README.md
├── run_app.bat
├── models/
│   └── best_model.keras
└── artifacts/
    ├── tokenizer.pkl
    ├── label_encoder.pkl
    └── config.json
```

## How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the Streamlit application:
   ```bash
   streamlit run app.py
   ```
   Or double-click `run_app.bat` on Windows!
