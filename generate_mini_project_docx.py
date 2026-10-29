import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os

def set_cell_background(cell, fill_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def style_header_cell(cell, text, width=None, align=WD_ALIGN_PARAGRAPH.LEFT):
    set_cell_background(cell, "1F4E79")
    set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(10)
    run.font.bold = True
    run.font.color.rgb = RGBColor(255, 255, 255)
    if width:
        cell.width = width

def style_body_cell(cell, text, fill_hex=None, bold=False, italic=False, color_rgb=None, width=None, align=WD_ALIGN_PARAGRAPH.LEFT):
    if fill_hex:
        set_cell_background(cell, fill_hex)
    set_cell_margins(cell, top=90, bottom=90, left=150, right=150)
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(str(text))
    run.font.name = "Calibri"
    run.font.size = Pt(9.5)
    run.font.bold = bold
    run.font.italic = italic
    if color_rgb:
        run.font.color.rgb = color_rgb
    else:
        run.font.color.rgb = RGBColor(40, 40, 40)
    if width:
        cell.width = width

def add_code_block(doc, code_str):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F4F6F9")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="BDC3C7"/>
            <w:left w:val="single" w:sz="18" w:space="0" w:color="1F4E79"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="BDC3C7"/>
            <w:right w:val="single" w:sz="6" w:space="0" w:color="BDC3C7"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(code_str.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(33, 47, 60)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_para(doc, text, bold_prefix=None, space_after=6, line_spacing=1.15):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(11)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(31, 78, 121)
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(40, 40, 40)
    return p

def add_chap_heading(doc, text):
    h = doc.add_heading(level=1)
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(8)
    run = h.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(15)
    run.font.bold = True
    run.font.color.rgb = RGBColor(31, 78, 121)
    return h

def add_sec_heading(doc, text):
    h = doc.add_heading(level=2)
    h.paragraph_format.space_before = Pt(10)
    h.paragraph_format.space_after = Pt(4)
    run = h.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(12.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(46, 117, 182)
    return h

def build_mini_report(output_path):
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p1.paragraph_format.space_before = Pt(10)
    p1.paragraph_format.space_after = Pt(2)
    r1 = p1.add_run("KARPAGAM COLLEGE OF ENGINEERING\n")
    r1.font.name = "Calibri"
    r1.font.size = Pt(18)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(31, 78, 121)

    r2 = p1.add_run("Rediscover | Refine | Redefine\nAccredited by NAAC with 'A+' grade\nAutonomous | Affiliated to Anna University\n(An ISO 9001:2015 and ISO 14001:2015 Certified Institution)\nCoimbatore – 641 032\n")
    r2.font.name = "Calibri"
    r2.font.size = Pt(10)
    r2.font.color.rgb = RGBColor(80, 80, 80)

    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.paragraph_format.space_after = Pt(20)
    r_div = p_div.add_run("―" * 55)
    r_div.font.color.rgb = RGBColor(46, 117, 182)
    r_div.font.bold = True

    p_app = doc.add_paragraph()
    p_app.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_app.paragraph_format.space_after = Pt(8)
    r_app = p_app.add_run("APPLICATION DEVELOPMENT III\n")
    r_app.font.name = "Calibri"
    r_app.font.size = Pt(13)
    r_app.font.bold = True
    r_app.font.color.rgb = RGBColor(100, 100, 100)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(28)
    r_title = p_title.add_run("SENTIMENT ANALYSIS OF TAMIL-ENGLISH (TANGLISH) CODE-MIXED TEXT USING DEEP RECURRENT NEURAL NETWORKS AND INTERACTIVE VOICE ASSISTANT")
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(15)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(192, 57, 43)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(16)
    r_sub = p_sub.add_run("Submitted by\n\n")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(11)
    r_sub.font.italic = True

    # Student Box Table
    st_tbl = doc.add_table(rows=2, cols=2)
    st_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    style_header_cell(st_tbl.cell(0, 0), "Candidate Name", width=Inches(3.2))
    style_header_cell(st_tbl.cell(0, 1), "Register Number", width=Inches(3.2))
    style_body_cell(st_tbl.cell(1, 0), "LATHIKA K", fill_hex="F2F4F7", bold=True, width=Inches(3.2))
    style_body_cell(st_tbl.cell(1, 1), "717824I132", fill_hex="F2F4F7", bold=True, width=Inches(3.2))
    set_table_borders(st_tbl, color="BDC3C7", sz="4", val="single")

    p_part = doc.add_paragraph()
    p_part.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_part.paragraph_format.space_before = Pt(30)
    p_part.paragraph_format.space_after = Pt(4)
    r_part = p_part.add_run(
        "In partial fulfillment for the award of the degree of\n"
        "BACHELOR OF TECHNOLOGY\nin\n"
        "ARTIFICIAL INTELLIGENCE AND DATA SCIENCE\n\n"
        "ANNA UNIVERSITY, CHENNAI – 600 028\n"
        "MAY 2026"
    )
    r_part.font.name = "Calibri"
    r_part.font.size = Pt(11)
    r_part.font.bold = True
    r_part.font.color.rgb = RGBColor(31, 78, 121)

    doc.add_page_break()

    # =========================================================================
    # BONAFIDE CERTIFICATE
    # =========================================================================
    p_bon_h = doc.add_paragraph()
    p_bon_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_bon_h.paragraph_format.space_before = Pt(14)
    p_bon_h.paragraph_format.space_after = Pt(2)
    r_bon_h = p_bon_h.add_run("KARPAGAM COLLEGE OF ENGINEERING\n")
    r_bon_h.font.name = "Calibri"
    r_bon_h.font.size = Pt(16)
    r_bon_h.font.bold = True
    r_bon_h.font.color.rgb = RGBColor(31, 78, 121)

    r_bon_sub = p_bon_h.add_run("Rediscover | Refine | Redefine\nAccredited by NAAC with 'A+' grade | Autonomous | Affiliated to Anna University\nCoimbatore – 641 032\n")
    r_bon_sub.font.name = "Calibri"
    r_bon_sub.font.size = Pt(10)
    r_bon_sub.font.color.rgb = RGBColor(90, 90, 90)

    p_bon_title = doc.add_paragraph()
    p_bon_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_bon_title.paragraph_format.space_before = Pt(20)
    p_bon_title.paragraph_format.space_after = Pt(20)
    r_bon_t = p_bon_title.add_run("BONAFIDE CERTIFICATE")
    r_bon_t.font.name = "Calibri"
    r_bon_t.font.size = Pt(14)
    r_bon_t.font.bold = True
    r_bon_t.font.color.rgb = RGBColor(31, 78, 121)

    p_bon_text = doc.add_paragraph()
    p_bon_text.paragraph_format.line_spacing = 1.3
    p_bon_text.paragraph_format.space_after = Pt(40)
    r_bon_body = p_bon_text.add_run(
        "This is to certify that the project report entitled \"SENTIMENT ANALYSIS OF TAMIL-ENGLISH (TANGLISH) CODE-MIXED TEXT "
        "USING DEEP RECURRENT NEURAL NETWORKS AND INTERACTIVE VOICE ASSISTANT\" submitted by LATHIKA K (Register No: 717824I132) "
        "is the bonafide work done by her in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology "
        "in Artificial Intelligence and Data Science at Karpagam College of Engineering, affiliated to Anna University, Chennai during the academic year 2025 – 2026."
    )
    r_bon_body.font.name = "Calibri"
    r_bon_body.font.size = Pt(11)

    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(80)
    r_sig = p_sig.add_run("Faculty Guide                                                                                              Head of the Department\n(Course In-charge)                                                                                         Dr. G. Vijaya, HoD / AI&DS")
    r_sig.font.name = "Calibri"
    r_sig.font.size = Pt(11)
    r_sig.font.bold = True

    doc.add_page_break()

    # =========================================================================
    # TABLE OF CONTENTS
    # =========================================================================
    add_chap_heading(doc, "TABLE OF CONTENTS")
    toc_items = [
        ("", "ACKNOWLEDGEMENT", "i"),
        ("", "ABSTRACT", "ii"),
        ("", "LIST OF FIGURES", "iii"),
        ("", "LIST OF ABBREVIATIONS", "iv"),
        ("1", "INTRODUCTION", "1"),
        ("1.1", "Key Components of the Tanglish Sentiment Analyzer", "2"),
        ("1.2", "Important Concepts in Code-Mixed Sentiment Analysis", "2"),
        ("1.3", "Types of Sentiment Classifications", "3"),
        ("1.4", "Tools and Technologies", "3"),
        ("1.5", "Development Process of Tanglish Sentiment Analyzer", "4"),
        ("2", "TOOLS AND TECHNOLOGY USED", "5"),
        ("2.1", "Front-End Development Tools", "5"),
        ("2.2", "Back-End / Deep Learning Tools", "6"),
        ("2.3", "Data Processing Tools", "6"),
        ("2.4", "Development Tools and Platforms", "7"),
        ("2.5", "Application Execution", "7"),
        ("3", "CASCADING STYLE SHEETS (CSS)", "8"),
        ("3.1", "CSS Syntax and Structure", "8"),
        ("3.2", "CSS in Tanglish Sentiment Analyzer Interface", "9"),
        ("3.3", "Typography and Real-Time Pulse Animations", "9"),
        ("4", "JAVASCRIPT & BROWSER WEB SPEECH API", "11"),
        ("4.1", "Key Characteristics of Client-Side JavaScript", "11"),
        ("4.2", "JavaScript in Tanglish Sentiment Analyzer", "12"),
        ("5", "MODEL IMPLEMENTATION", "14"),
        ("6", "CONCLUSION", "25"),
        ("7", "REFERENCES", "26")
    ]
    toc_tbl = doc.add_table(rows=len(toc_items) + 1, cols=3)
    toc_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    style_header_cell(toc_tbl.cell(0, 0), "CHAPTER NO", width=Inches(1.2))
    style_header_cell(toc_tbl.cell(0, 1), "TITLE", width=Inches(4.5))
    style_header_cell(toc_tbl.cell(0, 2), "PAGE NO", width=Inches(0.9), align=WD_ALIGN_PARAGRAPH.CENTER)
    for idx, (c_no, c_title, c_page) in enumerate(toc_items, start=1):
        bg = "F9FAFB" if idx % 2 == 1 else "FFFFFF"
        is_main = bool(c_no in ["1", "2", "3", "4", "5", "6", "7"] or not c_no)
        style_body_cell(toc_tbl.cell(idx, 0), c_no, fill_hex=bg, bold=is_main, width=Inches(1.2))
        style_body_cell(toc_tbl.cell(idx, 1), c_title, fill_hex=bg, bold=is_main, width=Inches(4.5))
        style_body_cell(toc_tbl.cell(idx, 2), c_page, fill_hex=bg, bold=is_main, align=WD_ALIGN_PARAGRAPH.CENTER, width=Inches(0.9))
    set_table_borders(toc_tbl, color="BDC3C7", sz="4", val="single")

    doc.add_page_break()

    # =========================================================================
    # ACKNOWLEDGEMENT & ABSTRACT
    # =========================================================================
    add_chap_heading(doc, "ACKNOWLEDGEMENT")
    add_para(doc, "First, I would like to express my sincere gratitude for the opportunity to carry out this Application Development III project with my own knowledge and faculty guidance. Although challenging, this has been an enriching experience that has allowed me to master natural language processing, deep recurrent neural architectures, and full-stack web speech deployment.")
    add_para(doc, "It is a moment of immense pride for me to reveal my profound thanks to our respected Principal, Dr. P. Karthigaikumar, who serves as a striving force in all our academic and technological endeavors.")
    add_para(doc, "I express my sincere thanks to Dr. G. Vijaya, Head of the Department of Artificial Intelligence and Data Science, for her continuous support and visionary academic environment.")
    add_para(doc, "I express my sincere thanks to my faculty guides and mentors who provided me with necessary guidance, technical insights, and constant encouragement throughout the design and testing phases of this project.")
    add_para(doc, "Finally, I acknowledge with due respect the unconditional love, patience, and moral support of my parents, which motivated me to achieve excellence.")

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    add_chap_heading(doc, "ABSTRACT")
    add_para(doc, "In the modern digital era, social media platforms in South Asia witness extensive user communication in code-mixed languages, particularly Tamil-English (Tanglish). In code-mixed text, regional Tamil phonetics and grammatical syntax are written using the Roman/Latin alphabet interspersed with English terms (e.g., 'Padam nalla illa aana acting super'). Traditional natural language processing models and standard English lexicons fail catastrophically on Tanglish due to non-standard orthography, post-positional negation (e.g., 'nalla illa' meaning 'not good'), and contrastive clauses bridging both praise and critique.")
    add_para(doc, "This project presents an end-to-end deep learning framework for Tanglish sentiment analysis that rigorously benchmarks seven recurrent neural architectures: Vanilla RNN, Bidirectional RNN (BiRNN), Long Short-Term Memory (LSTM), Gated Recurrent Unit (GRU), Bidirectional LSTM (BiLSTM), Sequence-to-Sequence (Seq2Seq), and BiLSTM with a custom Bahdanau Attention mechanism on the official DravidianCodeMix-FIRE 2020 benchmark dataset (43,991 YouTube comments across 5 classes). Data preprocessing techniques, including regex character elongation reduction (e.g., 'masssss' -> 'mass'), HTML entity decoding, Romanized contraction expansion, and dynamic sequence padding, are applied to optimize sequence quality.")
    add_para(doc, "Experimental results demonstrate that the BiLSTM with Bahdanau Attention mechanism achieves the champion performance among recurrent models with 61.65% Test Accuracy and 0.6056 Weighted F1-score on the 5-class classification task (+8.49% over standard BiLSTM). For binary polarity classification, a Hybrid CNN-BiLSTM achieves 85.54% – 86.10% accuracy with a 91.23% Positive F1-score.")
    add_para(doc, "Furthermore, to ensure hands-free accessibility for regional users, the system is deployed live on Streamlit Community Cloud featuring an Antigravity-style unified voice assistant. Built with the browser Web Speech API (ta-IN acoustic model), the interface enables real-time live voice typing word-by-word into a single input box, paired with Google Text-To-Speech (gTTS) verbal explanations. The deployed system provides actionable real-time sentiment intelligence for movie reviews, brand monitoring, and voice-assisted customer feedback.")

    doc.add_page_break()

    # =========================================================================
    # LIST OF FIGURES & LIST OF ABBREVIATIONS
    # =========================================================================
    add_chap_heading(doc, "LIST OF FIGURES")
    fig_tbl = doc.add_table(rows=6, cols=3)
    fig_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    style_header_cell(fig_tbl.cell(0, 0), "FIG NO", width=Inches(1.2))
    style_header_cell(fig_tbl.cell(0, 1), "FIGURE NAME", width=Inches(4.5))
    style_header_cell(fig_tbl.cell(0, 2), "PAGE NUMBER", width=Inches(0.9), align=WD_ALIGN_PARAGRAPH.CENTER)

    figs = [
        ("1.1", "Tanglish Sentiment Analyzer Process Architecture", "4"),
        ("5.1", "Index Page / Unified Voice & Text Interface", "19"),
        ("5.2", "Positive Sentiment Classification Output", "22"),
        ("5.3", "Negative Sentiment Classification with Negation Resolution", "23"),
        ("5.4", "Mixed Feelings Sentiment Output with Voice Explanation", "24")
    ]
    for idx, (f_no, f_name, f_p) in enumerate(figs, start=1):
        bg = "F9FAFB" if idx % 2 == 1 else "FFFFFF"
        style_body_cell(fig_tbl.cell(idx, 0), f_no, fill_hex=bg, bold=True, width=Inches(1.2))
        style_body_cell(fig_tbl.cell(idx, 1), f_name, fill_hex=bg, width=Inches(4.5))
        style_body_cell(fig_tbl.cell(idx, 2), f_p, fill_hex=bg, align=WD_ALIGN_PARAGRAPH.CENTER, width=Inches(0.9))
    set_table_borders(fig_tbl, color="BDC3C7", sz="4", val="single")

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    add_chap_heading(doc, "LIST OF ABBREVIATIONS")
    abbr_tbl = doc.add_table(rows=16, cols=2)
    abbr_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    style_header_cell(abbr_tbl.cell(0, 0), "ABBREVIATION", width=Inches(2.5))
    style_header_cell(abbr_tbl.cell(0, 1), "EXPANSION", width=Inches(4.1))

    abbrs = [
        ("NLP", "Natural Language Processing"),
        ("RNN", "Recurrent Neural Network"),
        ("BiRNN", "Bidirectional Recurrent Neural Network"),
        ("LSTM", "Long Short-Term Memory"),
        ("GRU", "Gated Recurrent Unit"),
        ("BiLSTM", "Bidirectional Long Short-Term Memory"),
        ("CNN", "Convolutional Neural Network"),
        ("Seq2Seq", "Sequence-to-Sequence"),
        ("HTML", "HyperText Markup Language"),
        ("CSS", "Cascading Style Sheets"),
        ("JS", "JavaScript"),
        ("TTS", "Text-To-Speech"),
        ("API", "Application Programming Interface"),
        ("UI / UX", "User Interface / User Experience"),
        ("OOV", "Out-Of-Vocabulary Token")
    ]
    for idx, (ab, exp) in enumerate(abbrs, start=1):
        bg = "F9FAFB" if idx % 2 == 1 else "FFFFFF"
        style_body_cell(abbr_tbl.cell(idx, 0), ab, fill_hex=bg, bold=True, width=Inches(2.5))
        style_body_cell(abbr_tbl.cell(idx, 1), exp, fill_hex=bg, width=Inches(4.1))
    set_table_borders(abbr_tbl, color="BDC3C7", sz="4", val="single")

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 1: INTRODUCTION
    # =========================================================================
    add_chap_heading(doc, "CHAPTER 1: INTRODUCTION")
    add_para(doc, "In today's interconnected digital ecosystem, multilingual social media communities frequently communicate using code-mixed languages. Code-mixing refers to the fluid alternation of linguistic units (words, phrases, and grammar) from two or more languages within a single conversation or sentence. In South India, especially across platforms like YouTube, Twitter/X, and Instagram, Tamil-English (Tanglish) represents the dominant informal medium of public expression. While users write using the Latin script, the underlying semantic and syntactic structures follow Tamil colloquial patterns.")
    add_para(doc, "The Tanglish Sentiment Analyzer application is engineered to analyze code-mixed opinions, movie reviews, and brand feedback using deep recurrent neural networks and speech technologies. The system ingests raw Romanized social text or continuous voice input, preprocesses linguistic idiosyncrasies, processes sequence representations, and classifies them into fine-grained sentiment categories: Positive, Negative, Mixed_feelings, unknown_state, and not-Tamil.")
    add_para(doc, "A primary innovation of this project is its accessibility layer: equipped with an Antigravity-style live voice assistant, users can speak naturally in Tamil or Tanglish without typing. Spoken words stream live word-by-word into the input box via the browser Web Speech API, and prediction outcomes are spoken aloud using Text-To-Speech (TTS).")

    add_sec_heading(doc, "1.1 Key Components of the Tanglish Sentiment Analyzer")
    add_para(doc, "The application comprises four primary architectural modules:\n"
                  "1. User Interface (Front-End): An interactive, dark-themed console combining text entry, live microphone speech streaming, quick sample chips, and Plotly confidence charts.\n"
                  "2. Deep Learning Inference Engine: Pre-trained recurrent and hybrid models (BiLSTM + Attention & CNN-BiLSTM) loaded into memory for real-time sequence classification.\n"
                  "3. Code-Mixed Linguistic Preprocessor: Sanitizes repeated characters ('semmaaaa' -> 'semma'), decodes HTML entities, expands contractions ('isn't' -> 'is not'), and handles post-positional negations ('nalla illa').\n"
                  "4. Voice Assistant Engine: Couples continuous Web Speech API (ta-IN acoustic model) for speech-to-text with Google Text-To-Speech (gTTS) for verbal feedback.")

    add_sec_heading(doc, "1.2 Important Concepts in Code-Mixed Sentiment Analysis")
    add_para(doc, "• Orthographic Normalization: Mitigating phonetic spelling variations without standardized dictionaries.\n"
                  "• Post-Positional Negation: In Tanglish, negation particles appear after the predicate ('nalla illa', 'seri illa'), requiring bidirectional context.\n"
                  "• Contrastive Clauses: Sentences containing 'aana', 'but', or 'irundhalum' bridge opposing polarities, demanding classification into Mixed_feelings.\n"
                  "• Bahdanau Attention: Dynamically assigns scalar weights to sentiment-carrying words while suppressing filler slang tokens ('da', 'pa', 'la').")

    add_sec_heading(doc, "1.3 Types of Sentiment Classifications")
    add_para(doc, "• Positive: Comments expressing explicit praise, enthusiasm, and satisfaction (e.g., 'Vijay is a good hero', 'movie semma super').\n"
                  "• Negative: Comments conveying strong criticism, dissatisfaction, or disappointment (e.g., 'padam nalla illa', 'waste of time').\n"
                  "• Mixed_feelings: Discourse containing balanced positive and negative aspects (e.g., 'Athula screenplay nalla illa aana acting nalla irunthuchu').\n"
                  "• unknown_state: Ambiguous statements, rhetorical queries, and slang without identifiable sentiment.\n"
                  "• not-Tamil: Comments typed purely in English, Hindi, or non-Dravidian scripts.")

    add_sec_heading(doc, "1.4 Tools and Technologies")
    add_para(doc, "• Python: Core programming language for deep learning and backend pipelines.\n"
                  "• TensorFlow / Keras: Building, training, and serializing recurrent neural models.\n"
                  "• Streamlit & Custom Components: Developing and hosting the interactive web interface.\n"
                  "• Web Speech API: Client-side real-time continuous speech recognition in ta-IN.\n"
                  "• gTTS: Text-to-speech audio feedback generation.\n"
                  "• Pandas & NumPy: Dataset loading, matrix operations, and array computations.")

    add_sec_heading(doc, "1.5 Development Process of Tanglish Sentiment Analyzer")
    add_para(doc, "1. Define code-mixed sentiment challenges and dataset requirements.\n"
                  "2. Collect and sanitize the official DravidianCodeMix-FIRE 2020 benchmark dataset.\n"
                  "3. Implement custom regex normalization and Keras Tokenizer sequence padding.\n"
                  "4. Train and benchmark 7 recurrent models + hybrid CNN-BiLSTM on GPU.\n"
                  "5. Evaluate confusion matrices, parameter counts, and inference latencies.\n"
                  "6. Develop the Antigravity-style unified voice and keyboard input custom component.\n"
                  "7. Integrate gTTS verbal feedback and Plotly probability visualizations.\n"
                  "8. Deploy to Streamlit Community Cloud and verify live real-time inference.")

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 2: TOOLS AND TECHNOLOGY USED
    # =========================================================================
    add_chap_heading(doc, "CHAPTER 2: TOOLS AND TECHNOLOGY USED")
    add_para(doc, "The Tanglish Sentiment Analyzer application utilizes deep learning, modern web frameworks, and speech synthesis pipelines to ensure robust inference and dynamic user experiences.")

    add_sec_heading(doc, "2.1 Front-End Development Tools")
    add_para(doc, "• HTML5 & CSS3: Establishes the structural layout and dark-mode styling for the web components.\n"
                  "• Streamlit (v1.35+): Primary Python web framework powering real-time inference and UI widgets.\n"
                  "• Streamlit Custom Components (declare_component): Bridges client-side JavaScript Web Speech API with Python backend via window.parent.postMessage.\n"
                  "• Plotly Express: Renders responsive horizontal probability distribution bar charts.")

    add_sec_heading(doc, "2.2 Back-End / Deep Learning Tools")
    add_para(doc, "• TensorFlow / Keras (v2.15+): Core engine for deep neural layers (Embedding, SimpleRNN, LSTM, GRU, Bidirectional, Conv1D, Attention).\n"
                  "• gTTS (Google Text-to-Speech): Generates dynamic MP3 audio streams for verbal output.\n"
                  "• NumPy: Performs tensor reshaping, padding, and probability softmax scaling.\n"
                  "• Pickle & JSON: Serializes vocabulary tokens, class label mappings, and model configurations.")

    add_sec_heading(doc, "2.3 Data Processing Tools")
    add_para(doc, "• Keras Tokenizer: Maps 25,000 top vocabulary tokens with an <OOV> fallback index.\n"
                  "• Pad Sequences: Post-pads and truncates all variable-length sentences to MAX_LEN=45 tokens.\n"
                  "• Regex Normalizer: Strips URLs, user handles, and compresses elongated character repetitions.")

    add_sec_heading(doc, "2.4 Development Tools and Platforms")
    add_para(doc, "• Visual Studio Code: Main integrated development environment (IDE).\n"
                  "• Git & GitHub: Version control repository (https://github.com/Lathika-Kumar/Tanglish-Sentiment-Analysis).\n"
                  "• Streamlit Community Cloud: Linux container hosting the live public application.")

    add_sec_heading(doc, "2.5 Application Execution")
    add_para(doc, "The web application can be launched in multiple environments:\n"
                  "1. Windows 1-Click: Double-click run_app.bat in the project directory.\n"
                  "2. Command Prompt / Terminal: Execute 'streamlit run app.py' to launch on http://localhost:8501.\n"
                  "3. Live Public Cloud: Open https://lathika-kumar-tanglish-sentiment-analysis-app-gpcnv7.streamlit.app/ in any modern browser.")

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 3: CASCADING STYLE SHEETS (CSS)
    # =========================================================================
    add_chap_heading(doc, "CHAPTER 3: CASCADING STYLE SHEETS (CSS)")
    add_para(doc, "Cascading Style Sheets (CSS) controls the presentation, visual hierarchy, and responsive aesthetics of the Tanglish Sentiment Analyzer. An Antigravity-style dark-mode interface (#161b22, #0d1117) was created to optimize visual comfort during real-time speech and text interaction.")

    add_sec_heading(doc, "3.1 CSS Syntax and Structure")
    add_para(doc, "CSS applies styling rules through selectors, properties, and values. In the voice component:\n"
                  "• Selector (.mic-button): Selects the circular floating microphone button.\n"
                  "• Properties: background-color: #21262d; border-radius: 50%; width: 42px; height: 42px;\n"
                  "• Hover Transitions: transform: scale(1.08); border-color: #58a6ff;")

    add_sec_heading(doc, "3.2 CSS in Tanglish Sentiment Analyzer Interface")
    add_para(doc, "• Glassmorphism Containers: Soft border outlines (rgba(255, 255, 255, 0.08)) and drop-shadows (box-shadow: 0 4px 16px rgba(0,0,0,0.3)).\n"
                  "• Quick Dialogue Chips: Rounded pill buttons (border-radius: 20px) allowing one-click testing of pre-configured sample dialogues.\n"
                  "• Gradient Call-To-Action Button: 'Analyze Sentiment' button styled with linear-gradient(135deg, #238636, #2ea043) for high prominence.")

    add_sec_heading(doc, "3.3 Typography and Real-Time Pulse Animations")
    add_para(doc, "When speech recognition begins, CSS keyframe animations provide immediate visual feedback:\n"
                  "@keyframes pulse-red {\n"
                  "  0% { box-shadow: 0 0 0 0 rgba(248, 81, 73, 0.7); transform: scale(1); }\n"
                  "  50% { box-shadow: 0 0 0 10px rgba(248, 81, 73, 0); transform: scale(1.08); }\n"
                  "  100% { box-shadow: 0 0 0 0 rgba(248, 81, 73, 0); transform: scale(1); }\n"
                  "}\n"
                  "This pulses the microphone in vibrant red while the acoustic listener is actively recording spoken Tanglish words.")

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 4: JAVASCRIPT & BROWSER WEB SPEECH API
    # =========================================================================
    add_chap_heading(doc, "CHAPTER 4: JAVASCRIPT & BROWSER WEB SPEECH API")
    add_para(doc, "JavaScript powers client-side interactivity, speech processing, and bi-directional communication between the custom component iframe and the Streamlit Python server.")

    add_sec_heading(doc, "4.1 Key Characteristics of Client-Side JavaScript")
    add_para(doc, "• Asynchronous Event Loop: Manages real-time audio streams without locking the browser UI thread.\n"
                  "• DOM Manipulation: Dynamically appends recognized words word-by-word into the <textarea> in real time.\n"
                  "• Custom PostMessage Protocol: Sends JSON payloads across iframes using window.parent.postMessage.")

    add_sec_heading(doc, "4.2 JavaScript in Tanglish Sentiment Analyzer")
    add_para(doc, "The component initializes the browser's native SpeechRecognition object configured to 'ta-IN' (Tamil & Tanglish acoustic model). As the user talks, interim and final speech transcripts stream live into the textarea:")
    
    js_code = r'''// Real-Time Web Speech Listener & Streamlit Custom Component Protocol
const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRec) {
    recognition = new SpeechRec();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'ta-IN';

    recognition.onresult = function(event) {
        let interimText = '';
        let finalChunk = persistentTranscript;
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                persistentTranscript += event.results[i][0].transcript + ' ';
                finalChunk = persistentTranscript;
            } else {
                interimText += event.results[i][0].transcript;
            }
        }
        // Streams words dynamically into the box as they are spoken!
        textarea.value = (finalChunk + interimText).trim();
    };
}

function triggerAnalyze() {
    // Sends value directly to Streamlit Python backend
    window.parent.postMessage({
        isStreamlitMessage: true,
        type: "streamlit:setComponentValue",
        value: { text: textarea.value.trim(), timestamp: Date.now() },
        dataType: "json"
    }, "*");
}'''
    add_code_block(doc, js_code)

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 5: MODEL IMPLEMENTATION
    # =========================================================================
    add_chap_heading(doc, "CHAPTER 5: MODEL IMPLEMENTATION")
    add_para(doc, "This chapter details the source code and implementation of the complete Tanglish Sentiment Analyzer, including the custom Web Speech component (index.html) and the primary Streamlit application (app.py).")

    add_sec_heading(doc, "5.1 Custom Front-End Component: index.html")
    add_para(doc, "The unified front-end component encapsulates the Antigravity-style voice assistant and keyboard entry into an autonomous web widget:")

    idx_code_sample = r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <style>
    body { background: transparent; font-family: -apple-system, sans-serif; color: #e6edf3; }
    .wrapper { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 16px; }
    textarea { width: 100%; min-height: 105px; background: #0d1117; color: #fff; border-radius: 10px; padding: 14px 54px 14px 14px; }
    .mic-button { position: absolute; right: 12px; bottom: 14px; width: 42px; height: 42px; border-radius: 50%; }
    .mic-button.recording { background: #da3633 !important; animation: pulse-red 1.5s infinite; }
  </style>
</head>
<body>
  <div class="wrapper" id="componentRoot">
    <textarea id="dialogueInput" placeholder="Type here with keyboard, OR click mic to speak live..."></textarea>
    <button id="micBtn" class="mic-button" onclick="toggleListening()">🎙️</button>
    <button class="analyze-btn" onclick="triggerAnalyze()">🔍 Analyze Sentiment</button>
  </div>
</body>
</html>'''
    add_code_block(doc, idx_code_sample)

    add_sec_heading(doc, "5.2 Primary Application Server: app.py")
    add_para(doc, "The Streamlit application coordinates artifact loading, model inference, linguistic rule calibration, and text-to-speech output:")

    app_code_sample = r'''import streamlit as st
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np, pandas as pd, pickle, json, re, io
import plotly.express as px
from gtts import gTTS
import streamlit.components.v1 as components

# Load Cached Model & Tokenizer
@st.cache_resource
def load_all_artifacts():
    model = load_model("models/best_model.keras", custom_objects={"AttentionLayer": AttentionLayer})
    with open("artifacts/tokenizer.pkl", "rb") as f: tokenizer = pickle.load(f)
    with open("artifacts/config.json", "r") as f: config = json.load(f)
    return model, tokenizer, config

# Declare Custom Component for Unified Voice & Keyboard Input
unified_voice_input = components.declare_component("unified_voice_input", path="./voice_input_component")
component_data = unified_voice_input(language="ta-IN", key="voice_widget")

if component_data and "text" in component_data:
    text = component_data["text"]
    seq = tokenizer.texts_to_sequences([clean_tanglish_text(text)])
    padded = pad_sequences(seq, maxlen=45, padding='post')
    raw_pred = model.predict(padded)[0]
    # Predict Sentiment & Generate Audio Explanation via gTTS
    st.metric("Predicted Sentiment", pred_label)
    st.audio(generate_speech(speech_text), format="audio/mp3", autoplay=True)'''
    add_code_block(doc, app_code_sample)

    add_sec_heading(doc, "5.3 Application Execution & Output Analysis")
    add_para(doc, "• FIGURE 5.1: Index Page — Displays the unified Antigravity-style input console with quick dialogue fill chips, live microphone listener, and benchmark sidebar statistics.\n"
                  "• FIGURE 5.2: Positive Sentiment — Verified with 'Vijay is a good hero' -> Output: Positive 🟢 (Confidence: 94.2%).\n"
                  "• FIGURE 5.3: Negative Sentiment — Verified with 'padam nalla illa' -> Output: Negative 🔴 (Confidence: 91.8%). Tanglish post-positional negation 'nalla illa' is accurately resolved.\n"
                  "• FIGURE 5.4: Mixed Feelings — Verified with 'I have recently watched a horror movie. Athula screenplay nalla illa aana acting nalla irunthuchu.' -> Output: Mixed_feelings 🟠 (Confidence: 88.5%). The assistant reads the linguistic rationale aloud via TTS.")

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 6: CONCLUSION & CHAPTER 7: REFERENCES
    # =========================================================================
    add_chap_heading(doc, "CHAPTER 6: CONCLUSION")
    add_para(doc, "The Tanglish Sentiment Analyzer project successfully addresses the real-world challenge of understanding informal, code-mixed social media communication in Tamil-English text. By collecting, cleaning, and preprocessing 43,991 comments from the DravidianCodeMix-FIRE 2020 dataset, the framework established comprehensive empirical benchmarks across seven recurrent neural architectures and a hybrid CNN-BiLSTM model.")
    add_para(doc, "Key conclusions established in this work include:\n"
                  "1. Attention Supremacy: Incorporating a trainable Bahdanau Attention mechanism with BiLSTM achieved 61.65% 5-class test accuracy, outperforming standard BiLSTM by +8.49% and Vanilla RNN by +20.10%.\n"
                  "2. Gating Necessity: Additive cell states in LSTM (52.27%) and GRU (51.50%) proved vital to retain sentiment across long code-mixed clauses, while GRU demonstrated a 25% faster training convergence.\n"
                  "3. High-Accuracy Polarity Benchmark: The Hybrid CNN-BiLSTM achieved 85.54% – 86.10% accuracy with a 91.23% Positive F1-score, establishing state-of-the-art polarity classification.\n"
                  "4. Accessibility via Voice Integration: The Antigravity-style voice assistant with browser Web Speech API (ta-IN) bridges the literacy barrier, allowing regional users to speak naturally and receive verbal sentiment explanations.")

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    add_chap_heading(doc, "CHAPTER 7: REFERENCES")
    refs = [
        "Chakravarthi, B. R., et al. (2020). Overview of the Track on Sentiment Analysis for Dravidian Languages in Code-Mixed Text. In Forum for Information Retrieval Evaluation (FIRE 2020), CEUR-WS.",
        "Bahdanau, D., Cho, K., & Bengio, Y. (2015). Neural Machine Translation by Jointly Learning to Align and Translate. International Conference on Learning Representations (ICLR 2015).",
        "Hochreiter, S., & Schmidhuber, J. (1997). Long Short-Term Memory. Neural Computation, 9(8), 1735-1780.",
        "Cho, K., et al. (2014). Learning Phrase Representations using RNN Encoder-Decoder for Statistical Machine Translation. EMNLP 2014.",
        "Schuster, M., & Paliwal, K. K. (1997). Bidirectional Recurrent Neural Networks. IEEE Transactions on Signal Processing, 45(11), 2673-2681.",
        "Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research.",
        "McKinney, W. (2010). Data Structures for Statistical Computing in Python. Proceedings of the 9th Python in Science Conference.",
        "Harris, C. R., et al. (2020). Array Programming with NumPy. Nature, 585(7825), 357-362.",
        "Streamlit Inc. (2024). Streamlit Documentation: Custom Components and Web Speech API Integration."
    ]
    for r in refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.line_spacing = 1.15
        r_run = p_ref.add_run("• " + r)
        r_run.font.name = "Calibri"
        r_run.font.size = Pt(10.5)

    doc.save(output_path)
    print(f"Successfully created mini project report at: {output_path}")

if __name__ == "__main__":
    out_file = r"D:\Projects\tanglish-sentiment-analysis\MINI_PROJECT_REPORT_TANGLISH_SENTIMENT_ANALYSIS.docx"
    build_mini_report(out_file)
