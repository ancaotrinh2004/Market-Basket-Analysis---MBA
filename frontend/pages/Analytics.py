"""
Analytics Dashboard Page
"""
import streamlit as st
import pandas as pd
from config import PAGE_CONFIG, CUSTOM_CSS
from utils.api_client import APIClient
from utils.visualizations import (
    plot_top_items,
    plot_distribution,
    plot_scatter,
    create_metrics_cards
)

st.set_page_config(**PAGE_CONFIG)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Get API client
if 'api_client' not in st.session_state:
    from config import API_URL
    st.session_state.api_client = APIClient(API_URL)

api = st.session_state.api_client

# Header
st.title("📈 Analytics Dashboard")
st.markdown("Visualize patterns and insights from association rules")

# Load Data Button
if st.button("🔄 Refresh Data", type="primary"):
    st.session_state.pop('analytics_data', None)
    st.rerun()

# Load data if not in session
if 'analytics_data' not in st.session_state:
    with st.spinner("Loading analytics data..."):
        st.session_state.analytics_data = {
            'stats': api.get_statistics(),
            'top_items': api.get_top_items(limit=30),
            'rules': api.get_rules(limit=1000)
        }

data = st.session_state.analytics_data

# Check if data loaded successfully
if not data['stats']:
    st.error("Failed to load data. Please check API connection.")
    st.stop()

# ============= SECTION 1: Key Metrics =============
st.subheader("📊 Key Metrics")

stats = data['stats']
st.markdown(create_metrics_cards(stats), unsafe_allow_html=True)

# Additional metrics in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Items",
        f"{stats.get('total_items', 0):,}"
    )

with col2:
    st.metric(
        "Min Confidence",
        f"{stats.get('min_confidence', 0):.1%}",
        help="Lowest confidence among all rules"
    )

with col3:
    st.metric(
        "Max Confidence", 
        f"{stats.get('max_confidence', 0):.1%}",
        help="Highest confidence among all rules"
    )

with col4:
    st.metric(
        "Avg Support",
        f"{stats.get('avg_support', 0):.2%}",
        help="Average support across all rules"
    )

st.divider()

# ============= SECTION 2: Top Items =============
st.subheader("🏆 Top 30 Most Frequent Items")

items_data = data['top_items'].get('items', [])

if items_data:
    # Create two columns for chart and table
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = plot_top_items(items_data[:30], "Top 30 Items by Frequency")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**Top 10 Items:**")
        df_top = pd.DataFrame(items_data[:10])
        st.dataframe(
            df_top,
            hide_index=True,
            use_container_width=True,
            column_config={
                "item_name": "Item",
                "frequency": st.column_config.NumberColumn(
                    "Frequency",
                    format="%d"
                )
            }
        )
else:
    st.warning("No items data available")

st.divider()

# ============= SECTION 3: Rules Distribution =============
st.subheader("📊 Rules Distribution Analysis")

rules_data = data['rules'].get('rules', [])

if rules_data:
    df_rules = pd.DataFrame(rules_data)
    
    # Three columns for distributions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig_conf = plot_distribution(
            df_rules['confidence'].tolist(),
            'confidence',
            'Confidence Distribution'
        )
        st.plotly_chart(fig_conf, use_container_width=True)
    
    with col2:
        fig_lift = plot_distribution(
            df_rules['lift'].tolist(),
            'lift',
            'Lift Distribution'
        )
        st.plotly_chart(fig_lift, use_container_width=True)
    
    with col3:
        fig_support = plot_distribution(
            df_rules['support'].tolist(),
            'support',
            'Support Distribution'
        )
        st.plotly_chart(fig_support, use_container_width=True)
    
    # Summary statistics table
    st.write("**Distribution Statistics:**")
    
    summary_stats = pd.DataFrame({
        'Metric': ['Confidence', 'Lift', 'Support'],
        'Mean': [
            df_rules['confidence'].mean(),
            df_rules['lift'].mean(),
            df_rules['support'].mean()
        ],
        'Median': [
            df_rules['confidence'].median(),
            df_rules['lift'].median(),
            df_rules['support'].median()
        ],
        'Std Dev': [
            df_rules['confidence'].std(),
            df_rules['lift'].std(),
            df_rules['support'].std()
        ],
        'Min': [
            df_rules['confidence'].min(),
            df_rules['lift'].min(),
            df_rules['support'].min()
        ],
        'Max': [
            df_rules['confidence'].max(),
            df_rules['lift'].max(),
            df_rules['support'].max()
        ]
    })
    
    # Format numbers
    summary_stats['Mean'] = summary_stats['Mean'].apply(lambda x: f"{x:.4f}")
    summary_stats['Median'] = summary_stats['Median'].apply(lambda x: f"{x:.4f}")
    summary_stats['Std Dev'] = summary_stats['Std Dev'].apply(lambda x: f"{x:.4f}")
    summary_stats['Min'] = summary_stats['Min'].apply(lambda x: f"{x:.4f}")
    summary_stats['Max'] = summary_stats['Max'].apply(lambda x: f"{x:.4f}")
    
    st.dataframe(summary_stats, hide_index=True, use_container_width=True)

else:
    st.warning("No rules data available")

st.divider()

# ============= SECTION 4: Confidence vs Lift Scatter =============
st.subheader("🎯 Confidence vs Lift Analysis")

if rules_data:
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        min_conf_filter = st.slider(
            "Filter by Min Confidence",
            0.0, 1.0, 0.0, 0.05,
            key='scatter_conf'
        )
    
    with col2:
        min_lift_filter = st.slider(
            "Filter by Min Lift",
            0.0, 10.0, 0.0, 0.5,
            key='scatter_lift'
        )
    
    # Filter data
    df_filtered = df_rules[
        (df_rules['confidence'] >= min_conf_filter) &
        (df_rules['lift'] >= min_lift_filter)
    ].copy()
    
    st.info(f"Showing {len(df_filtered)} rules (filtered from {len(df_rules)})")
    
    # Scatter plot
    fig_scatter = plot_scatter(df_filtered.to_dict('records'))
    if fig_scatter:
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Quadrant analysis
    st.write("**Quadrant Analysis:**")
    
    median_conf = df_filtered['confidence'].median()
    median_lift = df_filtered['lift'].median()
    
    q1 = len(df_filtered[(df_filtered['confidence'] >= median_conf) & 
                          (df_filtered['lift'] >= median_lift)])
    q2 = len(df_filtered[(df_filtered['confidence'] < median_conf) & 
                          (df_filtered['lift'] >= median_lift)])
    q3 = len(df_filtered[(df_filtered['confidence'] < median_conf) & 
                          (df_filtered['lift'] < median_lift)])
    q4 = len(df_filtered[(df_filtered['confidence'] >= median_conf) & 
                          (df_filtered['lift'] < median_lift)])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "High Conf, High Lift",
            q1,
            help="Best rules - strong and reliable"
        )
    
    with col2:
        st.metric(
            "Low Conf, High Lift",
            q2,
            help="Interesting but less reliable"
        )
    
    with col3:
        st.metric(
            "Low Conf, Low Lift",
            q3,
            help="Weak rules - consider removing"
        )
    
    with col4:
        st.metric(
            "High Conf, Low Lift",
            q4,
            help="Common patterns but not surprising"
        )

st.divider()

# ============= SECTION 5: Top Rules =============
st.subheader("🏅 Top 20 Rules by Lift")

if rules_data:
    df_top_rules = df_rules.nlargest(20, 'lift').copy()
    
    # Format for display
    df_top_rules['support'] = df_top_rules['support'].apply(lambda x: f"{x:.4f}")
    df_top_rules['confidence'] = df_top_rules['confidence'].apply(lambda x: f"{x:.2%}")
    df_top_rules['lift'] = df_top_rules['lift'].apply(lambda x: f"{x:.2f}")
    
    st.dataframe(
        df_top_rules[['antecedent', 'consequent', 'support', 'confidence', 'lift']],
        hide_index=True,
        use_container_width=True,
        column_config={
            "antecedent": "If (Antecedent)",
            "consequent": "Then (Consequent)",
            "support": "Support",
            "confidence": "Confidence",
            "lift": "Lift"
        }
    )

st.divider()

# ============= SECTION 6: Export Section =============
st.subheader("💾 Export Data")

col1, col2, col3 = st.columns(3)

with col1:
    if items_data:
        csv_items = pd.DataFrame(items_data).to_csv(index=False)
        st.download_button(
            "📥 Download Top Items",
            csv_items,
            "top_items.csv",
            "text/csv",
            use_container_width=True
        )

with col2:
    if rules_data:
        csv_rules = df_rules.to_csv(index=False)
        st.download_button(
            "📥 Download All Rules",
            csv_rules,
            "all_rules.csv",
            "text/csv",
            use_container_width=True
        )

with col3:
    if rules_data:
        csv_top_rules = df_top_rules.to_csv(index=False)
        st.download_button(
            "📥 Download Top Rules",
            csv_top_rules,
            "top_rules.csv",
            "text/csv",
            use_container_width=True
        )

# Info box
with st.expander("ℹ️ How to Interpret the Dashboard"):
    st.markdown("""
    ### Key Insights:
    
    1. **Top Items Chart**: Shows most frequently appearing items in rules
        - Higher frequency = more connections with other items
        - Good candidates for promotions and bundling
    
    2. **Distribution Charts**:
        - **Confidence**: Most rules should be >50% for reliability
        - **Lift**: Values >1 indicate positive correlation
        - **Support**: Shows how common the pattern is
    
    3. **Confidence vs Lift Scatter**:
        - **Top-right quadrant**: Best rules (high confidence + high lift)
        - **Size of bubbles**: Represents support (bigger = more common)
    
    4. **Quadrant Analysis**:
        - Focus on "High Conf, High Lift" rules for recommendations
        - "Low Conf, Low Lift" rules can be filtered out
    
    5. **Top Rules Table**: 
        - Prioritize rules with highest lift for strongest recommendations
        - Verify confidence is acceptable (typically >10%)
    """)