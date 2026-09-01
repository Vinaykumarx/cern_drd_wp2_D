import streamlit as st
import base64
import os
from pathlib import Path

# Provide access to the background assets
THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parents[1]

def inject_css():
    bg_css = ""
    bg_path = Path(PROJECT_ROOT) / "assets" / "cern_bg.png"
    if bg_path.exists():
        with open(bg_path, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode()
            bg_css = f'''
            .stApp {{
                background-image: linear-gradient(rgba(13, 17, 23, 0.85), rgba(13, 17, 23, 0.98)), url("data:image/png;base64,{b64_img}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            '''

    st.markdown(f"""
    <style>
    {bg_css}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    /* Chat bubble container width */
    [data-testid="stChatMessage"] > div {
        max-width: 1100px;
        margin-left: auto;
        margin-right: auto;
        font-family: 'Inter', 'Roboto', sans-serif;
    }

    /* Assistant bubble - scientific abstract style */
    .assistant-bubble {
        background: #111b26;
        padding: 16px 20px;
        border-radius: 4px;
        border-left: 4px solid #0053a1;
        border-top: 1px solid #1f2937;
        border-right: 1px solid #1f2937;
        border-bottom: 1px solid #1f2937;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #e6edf3;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.4);
    }

    /* User bubble - dark CERN blue */
    .user-bubble {
        background: #0053a1;
        color: #ffffff;
        padding: 12px 18px;
        border-radius: 4px;
        font-size: 0.95rem;
        border: 1px solid #003a72;
    }

    /* Card on right */
    .side-card {
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 4px;
        padding: 12px;
        margin-bottom: 1rem;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.5);
    }
    .side-title {
        font-weight: 600;
        margin-bottom: 4px;
    }

    .side-meta {
        font-size: 0.75rem;
        color: #6b7280;
        margin-bottom: 4px;
    }
    </style>
    """, unsafe_allow_html=True)
