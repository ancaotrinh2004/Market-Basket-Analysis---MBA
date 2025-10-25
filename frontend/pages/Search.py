"""
Search Rules Page
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
st.title("🔍 Search Association Rules")
st.markdown("Find rules containing specific items")

# Search Section
st.subheader("🔎 Search by Item")

col1, col2 = st.columns([3, 1])

with col1:
    search_term = st.text_input(
        "Enter item name:",
        placeholder="e.g., Milk, Bread, Apple",
        help="Search for rules containing this item (case-insensitive)"
    )

with col2:
    st.write("")
    st.write("")
    search_btn = st.button("🔍 Search", type="primary", use_container_width=True)

# Search Results
if search_btn and search_term:
    with st.spinner(f"Searching for rules containing '{search_term}'..."):
        result = api.search_rules(item=search_term, limit=200)
    
    rules = result.get('rules', [])
    total = result.get('total', 0)
    
    if rules:
        st.success(f"✅ Found {total} rules containing '{search_term}'")
        
        # Convert to DataFrame
        df = pd.DataFrame(rules)
        
        # Separate into two categories
        df_as_antecedent = df[df['antecedent'].str.contains(search_term, case=False, na=False)]
        df_as_consequent = df[df['consequent'].str.contains(search_term, case=False, na=False)]
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs([
            f"📤 As Antecedent ({len(df_as_antecedent)})",
            f"📥 As Consequent ({len(df_as_consequent)})",
            f"📊 All Results ({len(df)})"
        ])
        
        with tab1:
            st.markdown(f"**Rules where '{search_term}' appears in the antecedent (IF part)**")
            st.caption("These show what items are commonly bought AFTER buying this item")
            
            if not df_as_antecedent.empty:
                # Sort by lift
                df_display = df_as_antecedent.sort_values('lift', ascending=False).copy()
                
                # Format columns
                df_display['support'] = df_display['support'].apply(lambda x: f"{x:.4f}")
                df_display['confidence'] = df_display['confidence'].apply(lambda x: f"{x:.2%}")
                df_display['lift'] = df_display['lift'].apply(lambda x: f"{x:.2f}")
                
                st.dataframe(
                    df_display[['antecedent', 'consequent', 'support', 'confidence', 'lift']],
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "antecedent": "If Customer Buys",
                        "consequent": "Then Also Buys",
                        "support": "Support",
                        "confidence": "Confidence",
                        "lift": "Lift"
                    }
                )
                
                # Top 5 recommendations
                st.write("**Top 5 Items Often Bought Together:**")
                top_5 = df_as_antecedent.nlargest(5, 'lift')['consequent'].tolist()
                for i, item in enumerate(top_5, 1):
                    st.markdown(f"{i}. **{item}**")
            else:
                st.info(f"No rules found where '{search_term}' is in the antecedent")
        
        with tab2:
            st.markdown(f"**Rules where '{search_term}' appears in the consequent (THEN part)**")
            st.caption("These show what items customers typically buy BEFORE buying this item")
            
            if not df_as_consequent.empty:
                # Sort by lift
                df_display = df_as_consequent.sort_values('lift', ascending=False).copy()
                
                # Format columns
                df_display['support'] = df_display['support'].apply(lambda x: f"{x:.4f}")
                df_display['confidence'] = df_display['confidence'].apply(lambda x: f"{x:.2%}")
                df_display['lift'] = df_display['lift'].apply(lambda x: f"{x:.2f}")
                
                st.dataframe(
                    df_display[['antecedent', 'consequent', 'support', 'confidence', 'lift']],
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "antecedent": "If Customer Buys",
                        "consequent": "Then Also Buys",
                        "support": "Support",
                        "confidence": "Confidence",
                        "lift": "Lift"
                    }
                )
                
                # Top 5 trigger items
                st.write(f"**Top 5 Items That Lead to Buying '{search_term}':**")
                top_5 = df_as_consequent.nlargest(5, 'lift')['antecedent'].tolist()
                for i, item in enumerate(top_5, 1):
                    st.markdown(f"{i}. **{item}**")
            else:
                st.info(f"No rules found where '{search_term}' is in the consequent")
        
        with tab3:
            st.markdown("**All rules containing the search term**")
            
            # Format all results
            df_all = df.sort_values('lift', ascending=False).copy()
            df_all['support'] = df_all['support'].apply(lambda x: f"{x:.4f}")
            df_all['confidence'] = df_all['confidence'].apply(lambda x: f"{x:.2%}")
            df_all['lift'] = df_all['lift'].apply(lambda x: f"{x:.2f}")
            
            st.dataframe(
                df_all[['antecedent', 'consequent', 'support', 'confidence', 'lift']],
                hide_index=True,
                use_container_width=True
            )
            
            # Download button
            csv = df_all.to_csv(index=False)
            st.download_button(
                f"📥 Download Results for '{search_term}'",
                csv,
                f"rules_{search_term.lower().replace(' ', '_')}.csv",
                "text/csv",
                use_container_width=True
            )
        
        # Statistics
        st.divider()
        st.subheader("📊 Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Rules", len(df))
        
        with col2:
            st.metric("As Antecedent", len(df_as_antecedent))
        
        with col3:
            st.metric("As Consequent", len(df_as_consequent))
        
        with col4:
            avg_lift = df['lift'].mean()
            st.metric("Avg Lift", f"{avg_lift:.2f}")
        
    else:
        st.warning(f"😕 No rules found containing '{search_term}'")
        st.info("Try a different search term or check the spelling")

elif search_btn and not search_term:
    st.warning("⚠️ Please enter a search term")

# Quick Search Suggestions
st.divider()
st.subheader("💡 Quick Search Suggestions")

with st.spinner("Loading popular items..."):
    top_items_data = api.get_top_items(limit=20)
    top_items = [item['item_name'] for item in top_items_data.get('items', [])]

if top_items:
    st.write("Click on an item to search:")
    
    # Create buttons in rows of 4
    cols_per_row = 4
    for i in range(0, len(top_items), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(top_items):
                with col:
                    if st.button(
                        top_items[i + j],
                        key=f"quick_{i+j}",
                        use_container_width=True
                    ):
                        st.session_state.quick_search = top_items[i + j]
                        st.rerun()

# Handle quick search
if 'quick_search' in st.session_state:
    search_term = st.session_state.quick_search
    del st.session_state.quick_search
    st.rerun()

# Help Section
with st.expander("ℹ️ Search Tips"):
    st.markdown("""
    ### How to Use Search:
    
    1. **Enter item name**: Type any product name (partial match supported)
    2. **View results in tabs**:
        - **As Antecedent**: Shows what's bought AFTER this item
        - **As Consequent**: Shows what's bought BEFORE this item
        - **All Results**: Complete list of matching rules
    
    3. **Interpret results**:
        - Higher **lift** = stronger association
        - Higher **confidence** = more reliable rule
        - Check both tabs for complete insights
    
    ### Use Cases:
    
    - **Product Placement**: See what items are frequently bought together
    - **Cross-Selling**: Find complementary products
    - **Inventory Planning**: Understand product dependencies
    - **Marketing**: Create product bundles based on strong associations
    
    ### Examples:
    
    - Search "Milk" to see dairy-related patterns
    - Search "Bread" to find breakfast/lunch combinations
    - Search "Apple" to discover fruit purchase patterns
    """)