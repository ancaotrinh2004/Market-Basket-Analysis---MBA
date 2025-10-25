"""
Streamlit Main App - Home Page
"""
import streamlit as st
from config import API_URL, PAGE_CONFIG, CUSTOM_CSS, APP_TITLE
from utils.api_client import APIClient
from utils.visualizations import create_metrics_cards

# Page config
st.set_page_config(**PAGE_CONFIG)

# Custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize API client
if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient(API_URL)

api = st.session_state.api_client

# Header
st.markdown(f'<h1 class="main-header">🛒 {APP_TITLE}</h1>', unsafe_allow_html=True)

st.markdown("""
### Welcome to Market Basket Analysis System

This application provides intelligent product recommendations using **FP-Growth** association rules mining.

#### 🎯 Features:
- **Real-time Recommendations**: Get product suggestions based on current cart
- **Rules Explorer**: Browse and filter association rules
- **Analytics Dashboard**: Visualize patterns and statistics
- **Search**: Find rules for specific products

#### 📊 How it works:
1. **FP-Growth Algorithm** mines frequent patterns from transaction data
2. **Association Rules** are generated with confidence and lift metrics
3. **Recommendations** are ranked by lift score and confidence
""")

# API Status
st.divider()
st.subheader("🔌 System Status")

col1, col2 = st.columns(2)

with col1:
    health = api.health_check()
    
    if health.get('status') == 'healthy':
        st.success("✅ API Server: Connected")
    else:
        st.error("❌ API Server: Disconnected")

with col2:
    db_status = health.get('database', 'unknown')
    
    if db_status == 'connected':
        st.success("✅ Database: Connected")
    else:
        st.error("❌ Database: Disconnected")

# Statistics
st.divider()
st.subheader("📈 System Statistics")

if health.get('status') == 'healthy':
    stats = api.get_statistics()
    
    if stats:
        st.markdown(create_metrics_cards(stats), unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Items", stats.get('total_items', 0))
        
        with col2:
            st.metric(
                "Confidence Range",
                f"{stats.get('min_confidence', 0):.2%} - {stats.get('max_confidence', 0):.2%}"
            )
        
        with col3:
            st.metric(
                "Lift Range",
                f"{stats.get('min_lift', 0):.2f} - {stats.get('max_lift', 0):.2f}"
            )
    else:
        st.warning("No statistics available")
else:
    st.error("Cannot load statistics. Please check API connection.")

# Quick Start
st.divider()
st.subheader("🚀 Quick Start")

st.markdown("""
1. Go to **🎯 Recommendations** page to get product suggestions
2. Explore **📊 Rules Explorer** to browse all association rules
3. Check **📈 Analytics** for visualizations and insights
4. Use **🔍 Search** to find rules for specific products
""")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>Powered by <b>FP-Growth Algorithm</b> & <b>FastAPI</b></p>
    <p>Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)