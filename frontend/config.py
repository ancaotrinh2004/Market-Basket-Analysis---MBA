"""
Configuration for Streamlit app
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# App Configuration
APP_TITLE = os.getenv("APP_TITLE", "Market Basket Analysis")
APP_ICON = "🛒"

# Page Configuration
PAGE_CONFIG = {
    "page_title": APP_TITLE,
    "page_icon": APP_ICON,
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Styling
CUSTOM_CSS = """
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .recommendation-card {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #2ca02c;
    }
    .stButton>button {
        width: 100%;
    }
</style>
"""