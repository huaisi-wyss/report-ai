import streamlit as st
from openai import OpenAI

# 1. Page Configuration & Custom CSS (The "HTML/CSS" part)
st.set_page_config(page_title="Report Mirror AI", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stTextArea textarea {
        border-radius: 10px;
        border: 1px solid #dfe1e5;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #007bff;
        color: white;
        height: 3em;
        font-weight: bold;
    }
    .report-box {
        padding: 20px;
        background-color: white;
        border-radius: 15px;
        border-left: 5px solid #007bff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar - Logic & Inputs
with st.sidebar:
    st.title("⚙️ Configuration")
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    category = st.selectbox("Post Category", 
                            ["Product Centric", "Engagement/Community", "Contest/Giveaway", "Educational", "Brand Awareness"])
    st.info("This tool mirrors the tone of your sample report and applies it to new captions.")

# 3. Main Interface
st.title("📊 Simple Report Analyst")
st.caption("Upload your sample analysis and new captions to generate a consistent report.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Reference Style")
    sample_text = st.text_area("Paste a previous high-quality analysis here:", height=300, 
                               placeholder="e.g., 'The campaign achieved a 5% engagement rate... The tone was authoritative yet accessible...'")

with col2:
    st.subheader("New Data")
    new_captions = st.text_area("Paste new post captions here:", height=300,
                                placeholder="Post 1: [Caption text]\nPost 2: [Caption text]")

# 4. Processing Logic
if st.button("Generate Mirror Analysis"):
    if not api_key:
        st.error("Please enter your OpenAI API Key in the sidebar.")
    elif not sample_text or not new_captions:
        st.warning("Please fill in both text areas.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            
            with st.spinner("Analyzing style and synthesizing..."):
                prompt = f"""
                You are a professional social media data analyst.
                
                STYLE REFERENCE:
                {sample_text}
                
                NEW DATA TO ANALYZE (Category: {category}):
                {new_captions}
                
                TASK:
                Write a new analysis for the 'NEW DATA'. 
                - Match the exact vocabulary, sentence structure, and formatting of the 'STYLE REFERENCE'.
                - If the reference uses data-heavy jargon, do the same.
                - If the reference is concise and bulleted, follow that structure.
                """

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                
                result = response.choices[0].message.content
                
                st.divider()
                st.subheader("🚀 Generated Report")
                st.markdown(f'<div class="report-box">{result}</div>', unsafe_allow_html=True)
                
                st.download_button("Download Report as Text", result, file_name="analysis_report.txt")
                
        except Exception as e:
            st.error(f"An error occurred: {e}")