"""
Recommendations Page
"""
import streamlit as st
import pandas as pd
from config import PAGE_CONFIG, CUSTOM_CSS
from utils.api_client import APIClient
from utils.visualizations import plot_recommendation_scores

st.set_page_config(**PAGE_CONFIG)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Get API client from session state
if 'api_client' not in st.session_state:
    from config import API_URL
    st.session_state.api_client = APIClient(API_URL)

api = st.session_state.api_client

# Header
st.title("🎯 Product Recommendations")
st.markdown("Get intelligent product recommendations based on items in cart")

# Sidebar Settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    top_n = st.slider(
        "Number of Recommendations",
        min_value=1,
        max_value=20,
        value=5,
        help="How many products to recommend"
    )
    
    min_confidence = st.slider(
        "Minimum Confidence",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.05,
        help="Filter rules with confidence >= threshold"
    )
    
    min_lift = st.slider(
        "Minimum Lift",
        min_value=0.0,
        max_value=5.0,
        value=1.0,
        step=0.1,
        help="Filter rules with lift >= threshold"
    )

# Main Content
st.divider()

# Get available items
with st.spinner("Loading items..."):
    items_data = api.get_top_items(limit=100)
    available_items = [item['item_name'] for item in items_data.get('items', [])]

if not available_items:
    st.error("Cannot load items from API. Please check connection.")
    st.stop()

# Item Selection
st.subheader("🛒 Select Items in Cart")

col1, col2 = st.columns([3, 1])

with col1:
    selected_items = st.multiselect(
        "Choose products:",
        options=available_items,
        default=[],
        help="Select one or more items"
    )

with col2:
    st.write("")
    st.write("")
    clear_btn = st.button("🗑️ Clear All", use_container_width=True)
    if clear_btn:
        st.rerun()

# Display selected items
if selected_items:
    st.info(f"Selected {len(selected_items)} item(s): {', '.join(selected_items)}")

# Get Recommendations Button
st.divider()

if st.button("✨ Get Recommendations", type="primary", use_container_width=True):
    if not selected_items:
        st.warning("⚠️ Please select at least one item")
    else:
        with st.spinner("Generating recommendations..."):
            result = api.get_recommendations(
                items=selected_items,
                top_n=top_n,
                min_confidence=min_confidence,
                min_lift=min_lift
            )
        
        recommendations = result.get('recommended_items', [])
        
        if recommendations:
            st.success(f"✅ Found {len(recommendations)} recommendations!")
            
            # Display as cards
            st.subheader("📦 Recommended Products")
            
            for i, item in enumerate(recommendations, 1):
                with st.container():
                    st.markdown(f"""
                    <div class="recommendation-card">
                        <h3 style="color: #222222;">#{i} {item['item_name']}</h3>
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1rem;">
                            <div>
                                <p style="color: #666; margin: 0;">Score</p>
                                <p style="font-size: 1.5rem; font-weight: bold; margin: 0; color: #2ca02c;">
                                    {item['score']:.2f}
                                </p>
                            </div>
                            <div>
                                <p style="color: #666; margin: 0;">Confidence</p>
                                <p style="font-size: 1.5rem; font-weight: bold; margin: 0; color: #222222;">
                                    {item['confidence']:.1%}
                                </p>
                            </div>
                            <div>
                                <p style="color: #666; margin: 0;">Lift</p>
                                <p style="font-size: 1.5rem; font-weight: bold; margin: 0; color: #222222;">
                                    {item['lift']:.2f}
                                </p>
                            </div>
                            <div>
                                <p style="color: #666; margin: 0;">Matched Rules</p>
                                <p style="font-size: 1.5rem; font-weight: bold; margin: 0; color: #222222;">
                                    {item['matched_rules']}
                                </p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Visualization
            st.divider()
            st.subheader("📊 Visualization")
            
            fig = plot_recommendation_scores(recommendations)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Download
            st.divider()
            df = pd.DataFrame(recommendations)
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Recommendations (CSV)",
                data=csv,
                file_name="recommendations.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("😕 No recommendations found. Try adjusting the settings in sidebar.")

# Info Box
with st.expander("ℹ️ How Recommendations Work"):
    st.markdown("""
    ### Algorithm Explanation
    
    1. **Input**: Items currently in the cart
    2. **Process**: 
        - Find association rules where antecedent contains cart items
        - Filter by confidence and lift thresholds
        - Exclude items already in cart
        - Rank by average lift score
    3. **Output**: Top-N recommended products
    
    ### Metrics:
    - **Score**: Average lift across all matching rules (higher = stronger association)
    - **Confidence**: Probability of buying consequent given antecedent
    - **Lift**: How much more likely to buy together vs independently
    - **Matched Rules**: Number of rules that generated this recommendation
    """)