"""
Rules Explorer Page
"""
import streamlit as st
import pandas as pd
from config import PAGE_CONFIG, CUSTOM_CSS
from utils.api_client import APIClient

st.set_page_config(**PAGE_CONFIG)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Get API client
if 'api_client' not in st.session_state:
    from config import API_URL
    st.session_state.api_client = APIClient(API_URL)

api = st.session_state.api_client

# Header
st.title("📊 Association Rules Explorer")
st.markdown("Browse and filter FP-Growth association rules")

# Sidebar Filters
with st.sidebar:
    st.header("🔍 Filters")
    
    min_confidence = st.slider(
        "Min Confidence",
        0.0, 1.0, 0.0, 0.05
    )
    
    min_lift = st.slider(
        "Min Lift",
        0.0, 10.0, 0.0, 0.5
    )
    
    min_support = st.slider(
        "Min Support",
        0.0, 1.0, 0.0, 0.01
    )
    
    limit = st.selectbox(
        "Max Results",
        [50, 100, 200, 500, 1000],
        index=1
    )
    
    load_btn = st.button("🔄 Load Rules", type="primary", use_container_width=True)

# Main Content
if load_btn or 'rules_data' not in st.session_state:
    with st.spinner("Loading rules..."):
        result = api.get_rules(
            min_confidence=min_confidence,
            min_lift=min_lift,
            min_support=min_support,
            limit=limit
        )
        
        st.session_state.rules_data = result

# Display Rules
if 'rules_data' in st.session_state:
    result = st.session_state.rules_data
    rules = result.get('rules', [])
    total = result.get('total', 0)
    
    if rules:
        st.success(f"✅ Loaded {len(rules)} rules (Total matching: {total})")
        
        # Convert to DataFrame
        df = pd.DataFrame(rules)
        
        # Format columns
        df['support'] = df['support'].apply(lambda x: f"{x:.4f}")
        df['confidence'] = df['confidence'].apply(lambda x: f"{x:.2%}")
        df['lift'] = df['lift'].apply(lambda x: f"{x:.2f}")
        
        # Display table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "antecedent": "Antecedent (If)",
                "consequent": "Consequent (Then)",
                "support": "Support",
                "confidence": "Confidence",
                "lift": "Lift"
            }
        )
        
        # Download
        st.divider()
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download Rules (CSV)",
            csv,
            "association_rules.csv",
            "text/csv",
            use_container_width=True
        )
    else:
        st.warning("No rules found with current filters")
else:
    st.info("Click 'Load Rules' to fetch data")

# Info
with st.expander("ℹ️ Understanding Association Rules"):
    st.markdown("""
    ### Rule Format
    **Antecedent → Consequent**
    
    Example: `Milk → Bread`
    - If customer buys **Milk**, they are likely to buy **Bread**
    
    ### Metrics:
    - **Support**: How frequently the itemset appears (% of transactions)
    - **Confidence**: Probability of consequent given antecedent
    - **Lift**: Correlation strength (>1 = positive, =1 = independent, <1 = negative)
    """)