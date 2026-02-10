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

    mode_selection = st.selectbox(
        "📑 Output Mode",
        ["Auto", "Mode A - Itemised", "Mode B - Strategic Summary"],
        index=0
    )

# 3. Main Interface
st.title("📊 Social Media Report Generator")

# Section: The Gold Standard
sample_text = st.text_area("📋 Step 1: Insert Sample Analysis Structure (Gold Standard)", height=150, 
                           placeholder="Paste a previous analysis here. The AI will mimic this exact structure and tone.")

st.divider()

# Section: Dynamic Caption Input
st.subheader("📝 Step 2: Enter New Captions")
platform = st.selectbox(
    "📱 Platform",
    ["Instagram", "Facebook", "TikTok", "XHS", "YouTube"]
)

categories = sorted([
    "Branding", "Engagement", "Educational", "Product Centric",
    "Collaboration", "Contest", "Greetings",
    "Lifestyle", "Giveaway", "Campaign", "Memes", "Trivia",
    "Trendjacking", "Promotions", "New Outlet/ Grand Opening",
    "New Launch", "Festive", "Events", "Activations",
    "Recipes", "No Category"
])
# NEW: Define post formats
post_formats = sorted([
    "Static Post",
    "Carousel",
    "Animation",
    "Short Video",
    "Long Video"
])

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
            
            # ===== MODE LOGIC =====

            if mode_selection == "Mode A - Itemised":
                selected_mode = "A"
            elif mode_selection == "Mode B - Strategic Summary":
                selected_mode = "B"
            else:
                selected_mode = "AUTO"

            # CATEGORY ORDER ONLY NEEDED FOR MODE A
            if selected_mode == "A":
                CATEGORY_ORDER = categories
            elif selected_mode == "B":
                CATEGORY_ORDER = []
            else:
                CATEGORY_ORDER = categories  # Let AI decide but keep structure available

            grouped_data = defaultdict(list)
            for item in st.session_state.captions_list:
                if item["caption"].strip():
                    # Store both caption and its specific format
                    grouped_data[item["cat"]].append({
                        "text": item["caption"],
                        "format": item["format"]
                    })

            # ===== CATEGORY DISTRIBUTION =====
            category_counts = {}
            total_posts = 0

            for cat, items in grouped_data.items():
                count = len(items)
                category_counts[cat] = count
                total_posts += count

            category_percentage = {}
            for cat, count in category_counts.items():
                category_percentage[cat] = round((count / total_posts) * 100, 1) if total_posts > 0 else 0

            # ===== HEAVY CONTENT DETECTION =====

            branding_related = ["Branding", "Lifestyle", "Campaign", "Festive"]
            promo_related = ["Promotions", "Giveaway", "Contest", "New Launch"]

            branding_score = sum(category_counts.get(cat, 0) for cat in branding_related)
            promo_score = sum(category_counts.get(cat, 0) for cat in promo_related)

            content_focus = "Balanced"

            if branding_score > promo_score:
                content_focus = "Brand-heavy month"
            elif promo_score > branding_score:
                content_focus = "Promo-heavy month"

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
The text below represents the exact tone, sentence structure, and analytical depth to follow.
You must mirror this writing style precisely.
{sample_text}

STRICTNESS LEVEL:
- Very Safe: purely descriptive, no implied judgement.
- Balanced: light strategic framing.
- Strategic: clearer implication on brand and communication effectiveness.

Use level: {strictness}

SYSTEM MODE CONTROL:
User selected mode: {mode_selection}

If mode is Auto, decide intelligently.
If Mode A is selected, force Itemised Content Analysis.
If Mode B is selected, force Strategic Content Synthesis.

OUTPUT MODE SELECTION:
Determine the most appropriate analysis mode based on the input.

Mode A — Itemised Content Analysis
- Use when captions represent distinct executions or posts.
- Follow category structure strictly.
- Produce one analysis paragraph per caption.
- Explicitly identify the content format in each analysis.

Mode B — Strategic Content Synthesis
- Use when captions collectively describe a broader content ecosystem, platform role, or campaign narrative.
- IGNORE individual content categories.
- Analyse all captions holistically.
- Summarise recurring themes, execution patterns, platform roles, and communication objectives.
- Output several concise bullet points, each representing a key strategic insight.
- Do NOT force one bullet per caption.

If a human CA strategist would naturally summarise rather than itemise, you must do the same.

NEW CONTENT INPUT:
Each item includes a category and a caption.

{data_string}

STRICT RULES:
1. Mode A:
   - Group analysis under category headings using the SAME category names.
   - One analysis paragraph per caption.
2. Mode B:
   - Do NOT use category headings.
   - Output only synthesised bullet points.
3. IDENTIFICATION RULE:
   - Required in Mode A.
   - Optional in Mode B, only if it adds clarity.
4. Do NOT repeat, paraphrase, or rewrite caption text.
5. Do NOT add introductions, summaries, or conclusions.
6. Do NOT explain your thinking or methodology.
7. Match the tone, sentence length, and analytical depth of the REFERENCE exactly.
8. Keep language professional, objective, neutral, and CA-report ready.

OUTPUT FORMAT:
Mode A:
Category Heading
• Analysis paragraph

Mode B:
• Strategic synthesis bullet
• Strategic synthesis bullet
• Strategic synthesis bullet

Return ONLY the final analysis.
"""

            with st.spinner("Analyzing and grouping..."):
                response = model.generate_content(prompt)
                
            st.divider()
            st.subheader("📊 Content Distribution Overview")
            st.write(f"**Platform:** {platform}")
            st.write(f"**Content Focus:** {content_focus}")
            for cat, pct in sorted(category_percentage.items(), key=lambda x: x[1], reverse=True):
                st.write(f"{cat}: {pct}%")

            st.subheader("📈 Final Analysis")
            st.markdown(f'<div class="analysis-card">{response.text}</div>', unsafe_allow_html=True)
            st.download_button("Download Report", response.text, file_name="social_report.txt")

            st.info("⚠️ **Note:** This report is AI-generated. While designed to mirror professional standards, kindly review all outputs for accuracy and strategic alignment.")

        except Exception as e:
            st.error(f"Error: {e}")
        
st.divider()
st.caption("© 2026 Social Media Report Pro | AI-assisted reporting tool.")