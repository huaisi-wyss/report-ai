# 📊 Social Media Content Analysis (CA) Mirror

A professional-grade Streamlit application designed for agency-side strategists. This tool uses **Google Gemini 2.5 Flash-Lite** to analyze new social media captions while perfectly mirroring the tone, structure, and analytical depth of your "Gold Standard" sample reports.

## ✨ Features

* **Style Mirroring:** Analyzes new data based on a provided "Gold Standard" sample.
* **Dynamic Grouping:** Automatically categorizes analysis points (Branding, Engagement, Contest, etc.).
* **Strictness Control:** Toggle between *Very Safe* (descriptive) and *Strategic* (prescriptive) analysis modes.
* **Clean UI:** A modern, card-based dashboard for easy reading.
* **One-Click Export:** Download your generated report as a `.txt` or `.md` file.

## 🚀 Quick Start (Local/Codespaces)

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/report-ai.git
cd report-ai

```


2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Run the app:**
```bash
python3 -m streamlit run app.py

```



## ☁️ Deployment (Streamlit Cloud)

To publish this app permanently for free:

1. Connect your GitHub account to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Select this repository and the `app.py` file.
3. **Important:** Add your Google API Key in the **Advanced Settings > Secrets** section:
```toml
GEMINI_API_KEY = "your_google_api_key_here"

```



## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/)
* **AI Engine:** [Google Gemini 2.5 Flash-Lite](https://aistudio.google.com/)
* **Language:** Python 3.12+

## 📝 Usage Note

This tool is intended for internal agency review and client deck preparation. It ensures consistency across monthly reports by maintaining the established brand voice used in previous successful analyses.
