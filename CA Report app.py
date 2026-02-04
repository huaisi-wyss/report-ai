import streamlit as st
import google.generativeai as genai
from collections import defaultdict
import os
api_key = os.environ.get("GEMINI_API_KEY")

st.set_page_config(page_title="Social Media Report Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stTextArea textarea { border-radius: 8px; border: 1px solid #d1d9e0; }
    .analysis-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        line-height: 1.6;
        white-space: pre-wrap;
    }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #1a73e8; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("🛡️ Analysis Settings")
    strictness = st.select_slider(
        "✍️ Analysis Strictness",
        options=["Very Safe", "Balanced", "Strategic"],
        value="Balanced"
    )

# 3. Main Interface
st.title("📊 Tailored Report Generator")

# Section: The Gold Standard
sample_text = st.text_area("📋 Step 1: Insert Sample Analysis Structure (Gold Standard)", height=150, 
                           placeholder="Paste a previous analysis here. The AI will mimic this exact structure and tone.")

st.divider()

# Section: Dynamic Caption Input
st.subheader("📝 Step 2: Enter New Captions")
categories = ["Branding", "Engagement", "Educational", "Product Centric", "Collaboration", "Contest", "Greetings"]
# NEW: Define post formats
post_formats = ["Static Post", "Carousel", "Animation", "Short Video", "Long Video"]

if 'captions_list' not in st.session_state:
    st.session_state.captions_list = [{"caption": "", "cat": categories[0], "format": post_formats[0]}]

def add_caption():
    st.session_state.captions_list.append({"caption": "", "cat": categories[0], "format": post_formats[0]})

# Render inputs for each caption - Now using 3 columns
for i, item in enumerate(st.session_state.captions_list):
    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_a:
        item["caption"] = st.text_area(f"Caption {i+1}", value=item["caption"], height=100, key=f"cap_{i}")
    with col_b:
        item["cat"] = st.selectbox(f"Category {i+1}", categories, index=categories.index(item["cat"]), key=f"cat_{i}")
    with col_c:
        # NEW: Format selector
        item["format"] = st.selectbox(f"Format {i+1}", post_formats, index=post_formats.index(item["format"]), key=f"format_{i}")

st.button("➕ Add Another Caption", on_click=add_caption)

# 4. Processing Logic
if st.button("🚀 Generate Grouped Report"):
    if not api_key:
        st.error("Please enter your API Key in the sidebar.")
    elif not sample_text or not st.session_state.captions_list[0]["caption"]:
        st.warning("Please provide a sample and at least one caption.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            
            CATEGORY_ORDER = ["Branding", "Engagement", "Educational", "Product Centric", "Collaboration", "Contest", "Greetings"]

            grouped_data = defaultdict(list)
            for item in st.session_state.captions_list:
                if item["caption"].strip():
                    # Store both caption and its specific format
                    grouped_data[item["cat"]].append({
                        "text": item["caption"],
                        "format": item["format"]
                    })

            data_string = ""
            idx = 1
            for cat in CATEGORY_ORDER:
                if cat in grouped_data:
                    for entry in grouped_data[cat]:
                        # NEW: Explicitly pass format to the prompt
                        data_string += f"ITEM {idx} [Category: {cat}] [Format: {entry['format']}]: {entry['text']}\n"
                        idx += 1

            prompt = f"""
ROLE:
You are a senior agency-side Content Analysis (CA) strategist.
You write concise, professional CA reports for internal review and client decks.

REFERENCE (GOLD STANDARD):
{sample_text}

NEW CONTENT INPUT:
{data_string}

STRICTNESS LEVEL: {strictness}

STRICT RULES:
1. Group analysis under clear category headings using the SAME category names.
2. Each caption must generate ONE analysis paragraph.
3. IDENTIFICATION RULE: You MUST identify the specific content format in your analysis. Instead of saying "This post" or "The content," you must use the provided format, e.g., "A static post of...", "The carousel featuring...", or "A short video highlighting...".
4. Do NOT repeat or rewrite the caption.
5. Do NOT add introductions, summaries, or conclusions.
6. Do NOT explain your thinking or process.
7. Match the tone, sentence length, and analytical depth of the REFERENCE exactly.
8. Keep language professional, objective, and CA-report ready.

OUTPUT FORMAT:
Category Heading
• Analysis sentence

Return ONLY the grouped analysis.
"""

            with st.spinner("Analyzing and grouping..."):
                response = model.generate_content(prompt)
                
            st.divider()
            st.subheader("📈 Final Analysis")
            st.markdown(f'<div class="analysis-card">{response.text}</div>', unsafe_allow_html=True)
            st.download_button("Download Report", response.text, file_name="social_report.txt")

        except Exception as e:
            st.error(f"Error: {e}")